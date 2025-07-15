#
# remote connect to Gen2 observation
#
"""
Program to connect to Subaru Telescope Remote Observation Displays.

Requirements:
  See top-level file "install.txt"

Usage:
  Follow instructions in top-level file "instructions.txt".

  then:
  $ g2remote -f config.yml

  OR:
  $ g2remote -f config.toml

depending upon the suffix of your configuration file.

"""
# stdlib imports
import sys
import os
import platform
import subprocess
import threading
import time
import select
import socketserver
import glob
import http.server
try:
    import tomllib
    have_tomllib = True
except ImportError:
    have_tomllib = False

# 3rd party imports
import paramiko
import yaml
import pyotp
from jinja2 import Environment, FileSystemLoader

from g2remote.version import version
from g2remote import __file__
module_home, _ = os.path.split(__file__)
html_home = os.path.join(module_home, 'html')

env = Environment(loader=FileSystemLoader(html_home))
template = env.get_template('gen2_screens.html')


screens = [1, 2, 3, 4, 5, 6, 7, 8]
menu = """
Choose one of the following options:
c: connect
h: show this help message
q: quit
r: re-read config file
x: disconnect
"""

class G2Connect:

    def __init__(self, logger=None):
        self.logger = logger
        self.config_path = None
        self.config = {}
        self.client = None
        self.totp = None
        self.thread = []
        self.servers = []
        self.proc = {}
        self.ev_quit = threading.Event()
        self.debug = False
        self.vncserver_hostname = 'localhost'
        self.my_server = None

    def rdconfig(self, path):
        if self.logger is not None:
            self.logger.info(f"reading config file {path}")
        else:
            print(f"reading config file {path}")
        self.config_path = path
        with open(path, 'r') as in_f:
            buf = in_f.read()
        if path.endswith(".yml"):
            self.config = yaml.safe_load(buf)
        else:
            if not have_tomllib:
                raise ValueError("Need python 3.11 to read TOML configs")
            self.config = tomllib.loads(buf)

        if 'secret' in self.config:
            self.totp = pyotp.TOTP(self.config['secret'])
        self.debug = self.config.get('debug', False)
        MyHttpRequestHandler.vnc_passwd = self.get_passwd()

        # The hostname of the VNC server is normally 'localhost',
        # because that is how the SSH tunnel is set up. However, for
        # debugging, it will be convenient to be able to optionally specify the
        # hostname of the VNC server in the configuration file.
        self.vncserver_hostname = self.config.get('vncserver_hostname',
                                                  self.vncserver_hostname)

        # For Windows, we have to determine the filepath of the VNC viewer application.
        if self.get_system() == 'windows' and self.config.get('use_vnc', False):
            self.find_win_vncviewer()
            if self.debug:
                print('vncviewer is {}'.format(self.win_vncviewer))

        self.check_config()

        # return name of this config, if it has one
        if 'name' in self.config:
            return self.config['name']

    def find_win_vncviewer(self):
        # On Windows, determine the filepath of the VNC vieweer application.
        self.win_vncviewer = None
        # Check to see if there is an executable file associated
        # with the ".vnc" file extension.
        assoc = subprocess.run('ASSOC .vnc', shell=True,
                                stdout=subprocess.PIPE).stdout.decode().strip()
        if len(assoc) > 0:
            # An association was found. Get the filepath of the exectuable file.
            ext, val = assoc.split('=')
            ftype = subprocess.run('FTYPE {}'.format(val), shell=True,
                                    stdout=subprocess.PIPE).stdout.decode().strip()
            self.win_vncviewer = ftype.split('=', 1)[1].split(' -')[0]
        else:
            # No association was found. Look for a *viewer*.exe file in the
            # same directory where the configuration file was found. Choose the
            # first file that matches the glob pattern (*viewer*.exe).
            config_dir = os.path.dirname(self.config_path)
            viewer_filelist = glob.glob(os.path.join(config_dir, '*viewer*.exe'))
            if len(viewer_filelist) > 0:
                self.win_vncviewer = viewer_filelist[0]
            else:
                print('Warning: Could not find suitable VNC viewer in {}'.format(os.path.abspath(config_dir)))

        # TightVNC and RealVNC have different command-line
        # arguments to specify the configuration filename.
        # Determine whether the VNC viewer application is TightVNC or RealVNC
        # so that we can correctly set the command-line argument.
        if self.win_vncviewer:
            # The Windows "wmic" command requires that the
            # path separators be double backslashes.
            win_vncviewer_mod = self.win_vncviewer.replace('\\','\\\\')
            # Get the application manufacturer information from the executable file metadata.
            cmd = 'wmic Path CIM_DataFile WHERE Name={} Get Manufacturer'.format(win_vncviewer_mod)
            applic_man = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE).stdout.decode().strip()
            if applic_man.find('GlavSoft') >= 0:
                # TightVNC viewer uses -optionsfile to specify configuration file
                self.win_vnc_config_option = '-optionsfile='
            elif applic_man.find('RealVNC') >= 0:
                # RealVNC viewer uses -config to specify configuration file
                self.win_vnc_config_option = '-config '
            else:
                print('Warning: Could not determine VNC viewer type from {}'.format(self.win_vncviewer))

    def check_config(self):
        # double-check some problematic things that can go wrong
        system = self.get_system()

        ssh_file = self.config['ssh_key']
        if not os.path.exists(ssh_file):
            if self.logger is not None:
                self.logger.error(f"'ssh_key': doesn't seem to refer to an existing file: {ssh_file}")
            else:
                print(f"'ssh_key': doesn't seem to refer to an existing file: {ssh_file}")

        # users need to have a VNC password
        vncpwd = self.config.get('vnc_passwd', '')
        if len(vncpwd) == 0:
            if self.logger is not None:
                self.logger.error("'vnc_passwd': doesn't seem to have a password")
            else:
                print("'vnc_passwd': doesn't seem to have a password")

        if self.config.get('use_vnc', False):
            vncpwd_file = self.config['vnc_passwd_file']
            if os.path.exists(vncpwd_file):
                # For Windows, we need to read in the password from the VNC password
                # file so that we can write a configuration file for the VNC
                # viewer application.
                if self.get_system() == 'windows':
                    with open(vncpwd_file, 'rb') as f:
                        self.vncpwd = f.read()
                    vncpwd_array = ['{:02x}'.format(item) for item in self.vncpwd]
                    self.vncpwd_str = ''.join(vncpwd_array)
            else:
                if self.logger is not None:
                    self.logger.error(f"'vnc_passwd_file': doesn't seem to refer to an existing file: {vncpwd_file}")
                else:
                    print(f"'vnc_passwd_file': doesn't seem to refer to an existing file: {vncpwd_file}")

    def write_win_vnc_config_file(self, num):
        # For Windows, write a VNC viewer configuration file into the same directory
        # where the config.yml file is located.
        config_dir = os.path.dirname(self.config_path)
        self.win_vnc_config_filepath = os.path.join(config_dir, 'vnc_config_file.vnc')
        try:
            with open(self.win_vnc_config_filepath, 'w') as f:
                print("""
                [connection]
                host={}
                port=590{}
                password={}
                [options]
                viewonly=1
                fitwindow=1
                WarnUnencrypted=0
                Quality=High
                """.format(self.vncserver_hostname, num, self.vncpwd_str), file=f)
        except Exception as e:
            print('Error: Unable to open {} for writing VNC viewer configuration file'.format(self.win_vnc_config_filepath))
            raise(e)

    def connect(self):
        self.ev_quit.clear()

        # make ssh connection
        if self.debug:
            paramiko.common.logging.basicConfig(level=paramiko.common.DEBUG)
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        #client.set_missing_host_key_policy(paramiko.WarningPolicy())
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client = client

        kwargs = dict(username=self.config['user'],
                      key_filename=self.config['ssh_key'],
                      look_for_keys=False,
                      allow_agent=False)
        if self.totp is not None:
            kwargs['password'] = self.totp.now()

        if self.logger is not None:
            self.logger.info("connecting ...")
        else:
            print("connecting ...")
        try:
            client.connect(self.config['server'], self.config['port'],
                           **kwargs)
        except Exception as e:
            raise Exception("*** Failed to connect to %s:%d: %r" % (
                self.config['server'], self.config['port'], e))

        # only start as many forwards as we need to for VNC screens
        _screens = screens
        if 'screens' in self.config:
            _screens = []
            for key in self.config['screens']:
                if key.startswith('screen_'):
                    _, num = key.split('_')
                    _screens.append(int(num))

        # set up threads for all the port forwards
        self.thread = []

        if self.config.get('use_vnc', False):
            # set up VNC forwards
            for num in _screens:
                port = 5900 + num
                t = threading.Thread(target=self.forward_tunnel,
                                     args=(port, 'localhost', port,
                                           client.get_transport()))
                t.start()
                self.thread.append(t)

        if self.config.get('use_novnc', True):
            # set up noVNC forwards
            for num in _screens:
                port = 6080 + num
                t = threading.Thread(target=self.forward_tunnel,
                                     args=(port, 'localhost', port,
                                           client.get_transport()))
                t.start()
                self.thread.append(t)

            # set up local http server
            port = 8500
            http_server = socketserver.TCPServer(("localhost", port),
                                                 MyHttpRequestHandler)
            t = threading.Thread(target=http_server.serve_forever,
                                 args=[])
            t.start()
            self.servers.append(http_server)
            self.thread.append(t)
            if self.logger is None:
                print("Visit http://localhost:8500/ to view screens via web browser.")
                print("")

        if self.config.get('use_sound', True):
            # set up sound forward
	    # WebRTC (gen2 sound)
            t = threading.Thread(target=self.forward_tunnel,
                                 args=(8889, 'localhost', 8889,
                                       client.get_transport()))
            t.start()
            self.thread.append(t)

    def forward_tunnel(self, local_port, remote_host, remote_port,
                       transport):
        # hack to pass some extra items to be used inside the handler
        class MyHandler(ForwardHandler):
            chain_host = remote_host
            chain_port = remote_port
            ssh_transport = transport
            ssh_transport.window_size = 2147483647

        fws = ForwardServer(("localhost", local_port), MyHandler)
        fws.ev_quit = self.ev_quit
        self.servers.append(fws)
        fws.serve_forever(poll_interval=0.5)

    def disconnect(self):
        if self.logger is not None:
            self.logger.info("disconnecting...")
        else:
            print("disconnecting...")
        self.ev_quit.set()

        self.stop_all()

        # shutdown all forwarders
        for s in self.servers:
            try:
                s.shutdown()
            except:
                pass
        self.servers = []

        for t in self.thread:
            t.join()
        self.thread = []

    def display(self, num):
        if not self.config.get('use_vnc', False):
            print(f"VNC viewer feature is not enabled; use web interface")
            return
        if self.logger is not None:
            self.logger.info(f"attempting to start VNC sessions for screen {num}")
        else:
            print(f"attempting to start VNC sessions for screen {num}")
        self.start_display(num)

    def get_geometry(self, num):
        """Get the local screen position for screen `num` from config
        file, if available, else return None.
        """
        geom = None
        if 'screens' not in self.config:
            return geom
        name = f"screen_{num}"
        screens = self.config['screens']

        if name in screens:
            info = screens[name]
            geom = info.get('geometry', None)
        return geom

    def start_display(self, num):
        system = self.get_system()

        args = []
        geom = self.get_geometry(num)

        if system == 'linux':
            if geom is not None:
                args.extend(['-geometry', geom])
            vncpwd = self.config['vnc_passwd_file']
            args.extend(['-passwd', vncpwd])
            args = ['vncviewer'] + args + ['{}:{}'.format(self.vncserver_hostname, num)]

        elif system == 'darwin':
            # <-- Mac OS X
            user = self.config['user']
            passwd = self.get_passwd()
            port = 5900 + num
            args = ['open', '-g',
                    "vnc://{}:{}@{}:{}".format(user, passwd, self.vncserver_hostname, port)]

        elif system == 'windows':
            self.write_win_vnc_config_file(num)
            # Note: Windows seems to prefer that the command and arguments
            # are supplied in a single string
            args = '{} {}{}'.format(self.win_vncviewer, self.win_vnc_config_option, self.win_vnc_config_filepath)

        procname = 'screen_{}'.format(num)

        if self.debug:
            print('args are {}'.format(args))

        self.proc[procname] = subprocess.Popen(args, stdin=subprocess.PIPE,
                                               stdout=subprocess.PIPE,
                                               stderr=subprocess.PIPE)

        time.sleep(1)
        res = self.proc[procname].poll()
        if res is not None and res != 0:
            if self.logger is not None:
                self.logger.error(f"hmm, VNC viewer appears to have exited with result {res}")
            else:
                print(f"hmm, VNC viewer appears to have exited with result {res}")
                print("stdout:\n" + self.proc[procname].stdout.read().decode())
                print("stderr:\n" + self.proc[procname].stderr.read().decode())

    def get_passwd(self):
        return self.config['vnc_passwd']

    def get_screens(self):
        screens = []
        if 'screens' not in self.config:
            return screens
        for name in self.config['screens']:
            name, num = name.split('_')
            num = int(num)
            screens.append(num)
        return screens

    def start_all(self):
        screens = self.get_screens()
        if len(screens) == 0:
            if self.logger is not None:
                self.logger.error("No screens found in config file!")
            else:
                print("No screens found in config file!")
            return

        for num in screens:
            self.start_display(num)

    def stop_display(self, num):
        procname = f'screen_{num}'

        if procname in self.proc:
            p = self.proc[procname]
            del self.proc[procname]
            p.kill()

    def stop_all(self):
        # shutdown all VNCs
        for k, p in list(self.proc.items()):
            del self.proc[k]
            try:
                p.kill()
            except Exception as e:
                pass
        self.proc = {}

    def get_system(self):
        system = platform.system().lower()
        return system

    def cmd_loop(self):
        digits = ["{}".format(num) for num in screens]
        print(menu)

        while True:
            sys.stdout.write("g2connect> ")
            sys.stdout.flush()
            ans = sys.stdin.readline().strip()

            try:
                if len(ans) == 0:
                    continue

                elif ans == 'q':
                    break

                elif ans in ('h', '?'):
                    print(menu)

                elif ans == 'r':
                    self.rdconfig(self.config_path)

                elif ans == 'c':
                    self.connect()

                elif ans == 'x':
                    self.disconnect()

                elif ans == 'a':
                    self.start_all()

                elif ans in digits:
                    self.display(int(ans))

                else:
                    print("I don't know that command. Type 'h' for a menu.")

            except KeyboardInterrupt:
                print("Caught keyboard interrupt!")
                return

            except Exception as e:
                print("Exception running command: {}".format(e))
                # TODO: traceback

        self.disconnect()


class ForwardServer(socketserver.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True


class ForwardHandler(socketserver.BaseRequestHandler):
    def handle(self):
        try:
            chan = self.ssh_transport.open_channel("direct-tcpip",
                                                   (self.chain_host,
                                                    self.chain_port),
                                                   self.request.getpeername())
        except Exception as e:
            print("Forwarding request failed: %r" % (e))
            return

        if chan is None:
            print("Forwarding request was rejected by the server.")
            return

        # ferry forwarding traffic
        pkt_size = 8192
        while not self.server.ev_quit.is_set():
            r, w, x = select.select([self.request, chan], [], [])
            if self.request in r:
                data = self.request.recv(pkt_size)
                if len(data) == 0:
                    break
                chan.send(data)
            if chan in r:
                data = chan.recv(pkt_size)
                if len(data) == 0:
                    break
                self.request.send(data)

        chan.close()
        self.request.close()


class MyHttpRequestHandler(http.server.BaseHTTPRequestHandler):

    # vars to pass to template
    vnc_passwd = ''

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self): # handle GET request
        vnc_passwd = self.vnc_passwd
        self._set_headers()
        self.wfile.write(template.render(vncpass=vnc_passwd).encode())


def main(options, args):

    print("g2remote v{}".format(version))
    if options.showversion:
        sys.exit(0)

    if options.config is None or not os.path.exists(options.config):
        print("Please specify location of config file with -f")
        sys.exit(1)

    g2c = G2Connect()
    g2c.rdconfig(options.config)
    g2c.check_config()

    g2c.cmd_loop()
