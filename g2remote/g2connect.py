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

# 3rd party imports
import paramiko
import yaml
import pyotp

screens = [1, 2, 3, 4, 5, 6, 7, 8]
menu = """
Choose one of the following options:
c: connect
h: show this help message
N: (digit from 1-8): open screen N
s: open sound player
q: quit
r: re-read config file
x: disconnect
"""

class G2Connect:

    def __init__(self):
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

    def rdconfig(self, path):
        print("reading config file {}".format(path))
        self.config_path = path
        with open(path, 'r') as in_f:
            self.config = yaml.safe_load(in_f)

        self.totp = pyotp.TOTP(self.config['secret'])
        self.debug = self.config.get('debug', False)

        # The hostname of the VNC server is normally 'localhost',
        # because that is how the SSH tunnel is set up. However, for
        # debugging, it will be convenient to be able to optionally specify the
        # hostname of the VNC server in the configuration file.
        self.vncserver_hostname = self.config.get('vncserver_hostname', self.vncserver_hostname)

        # For Windows, we have to determine the filepath of the VNC viewer application.
        if self.get_system() == 'windows':
            self.find_win_vncviewer()
            if self.debug:
                print('vncviewer is {}'.format(self.win_vncviewer))

        self.check_config()

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
            print("'ssh_key': doesn't seem to refer to an existing file: %s" % (
                ssh_file))

        if system in ['darwin']:
            # mac users need to have a VNC password
            vncpwd = self.config.get('vnc_passwd', '')
            if len(vncpwd) == 0:
                print("'vnc_passwd': doesn't seem to have a password")

        else:
            # non-mac users need to have a viable VNC password file
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
                print("'vnc_passwd_file': doesn't seem to refer to an existing file: %s" % (
                    vncpwd_file))

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

        print("connecting ...")
        try:
            client.connect(self.config['server'], self.config['port'],
                           username=self.config['user'],
                           key_filename=self.config['ssh_key'],
                           look_for_keys=False,
                           password=self.totp.now())
        except Exception as e:
            raise Exception("*** Failed to connect to %s:%d: %r" % (
                self.config['server'], self.config['port'], e))

        # set up threads for all the port forwards
        self.thread = []
        for num in screens:
            port = 5900 + num
            t = threading.Thread(target=self.forward_tunnel,
                                 args=(port, 'localhost', port,
                                       client.get_transport()))
            t.start()
            self.thread.append(t)

        # sound forward
        port = 8554
        t = threading.Thread(target=self.forward_tunnel,
                             args=(port, 'localhost', port,
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

        fws = ForwardServer(("", local_port), MyHandler)
        fws.ev_quit = self.ev_quit
        self.servers.append(fws)
        fws.serve_forever(poll_interval=0.5)

    def disconnect(self):
        print("disconnecting...")
        self.ev_quit.set()

        # shutdown all VNCs
        for k, p in list(self.proc.items()):
            del self.proc[k]
            p.kill()
        self.proc = {}

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
        print("attempting to start VNC sessions...")
        system = self.get_system()

        if system == 'linux':
            vncpwd = self.config['vnc_passwd_file']
            args = ['vncviewer', '-passwd', vncpwd, '{}:{}'.format(self.vncserver_hostname, num)]

        elif system == 'darwin':
            # <-- Mac OS X
            user = self.config['user']
            passwd = self.config['vnc_passwd']
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
            print("hmm, VNC viewer appears to have exited with result {}".format(res))
            print("stdout:\n" + proc[procname].stdout.read().decode())
            print("stderr:\n" + proc[procname].stderr.read().decode())


    def start_sound(self):
        print("attempting to start sound player...")
        procname = 'sound'
        args = ['ffplay', '-nostats', '-rtsp_transport', 'tcp', 'rtsp://localhost:8554/stream']
        if self.debug:
            print('args are {}'.format(args))

        self.proc[procname] = subprocess.Popen(args, stdin=subprocess.PIPE,
                                               stdout=subprocess.PIPE,
                                               stderr=subprocess.PIPE)

        time.sleep(2)
        res = self.proc[procname].poll()
        if res is not None and res != 0:
            print("hmm, ffplay appears to have exited with result {}".format(res))
            print("stdout:\n" + proc[procname].stdout.read().decode())
            print("stderr:\n" + proc[procname].stderr.read().decode())

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

                elif ans == 'a':
                    print(self.totp.now())

                elif ans == 'r':
                    self.rdconfig(self.config_path)

                elif ans == 'c':
                    self.connect()

                elif ans == 's':
                    self.start_sound()

                elif ans == 'x':
                    self.disconnect()

                elif ans == 'w':
                    from g2remote import remmina
                    remmina.write_gen2_screens(screens, self.config)

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
        while not self.server.ev_quit.is_set():
            r, w, x = select.select([self.request, chan], [], [])
            if self.request in r:
                data = self.request.recv(1024)
                if len(data) == 0:
                    break
                chan.send(data)
            if chan in r:
                data = chan.recv(1024)
                if len(data) == 0:
                    break
                self.request.send(data)

        chan.close()
        self.request.close()


def main(options, args):

    if options.config is None or not os.path.exists(options.config):
        print("Please specify location of config file with -f")
        sys.exit(1)

    g2c = G2Connect()
    g2c.rdconfig(options.config)

    g2c.cmd_loop()
