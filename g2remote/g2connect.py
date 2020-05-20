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

# 3rd party imports
import paramiko
import yaml
import pyotp

screens = [0, 1, 2, 3, 4, 5, 6, 7, 8]
menu = """
Choose one of the following options:
c: connect
h: show this help message
N: (digit from 1-8): open screen N
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

    def rdconfig(self, path):
        print("reading config file {}".format(path))
        self.config_path = path
        with open(path, 'r') as in_f:
            self.config = yaml.safe_load(in_f)

        self.totp = pyotp.TOTP(self.config['secret'])
        self.debug = self.config.get('debug', False)

        self.check_config()

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
            # non-mac users need to have a viable VNC config file
            vncpwd_file = self.config['vnc_passwd_file']
            if not os.path.exists(vncpwd_file):
                print("'vnc_passwd_file': doesn't seem to refer to an existing file: %s" % (
                    vncpwd_file))

    def connect(self):
        self.ev_quit.clear()

        # make ssh connection
        if self.debug:
            paramiko.common.logging.basicConfig(level=paramiko.common.DEBUG)
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.WarningPolicy())
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
            args = ['vncviewer', '-passwd', vncpwd, 'localhost:{}'.format(num)]

        elif system == 'darwin':
            # <-- Mac OS X
            user = self.config['user']
            passwd = self.config['vnc_passwd']
            port = 5900 + num
            args = ['open', '-n', '-g',
                    "vnc://{}:{}@localhost:{}".format(user, passwd, port)]

        elif system == 'windows':
            vncpwd = self.config['vnc_passwd_file']
            args = ['vncviewer', '-passwd', vncpwd, 'localhost:{}'.format(num)]

        procname = 'screen_{}'.format(num)

        self.proc[procname] = subprocess.Popen(args, stdin=subprocess.PIPE,
                                               stdout=subprocess.PIPE,
                                               stderr=subprocess.PIPE)

        time.sleep(1)
        res = self.proc[procname].poll()
        if res is not None and res != 0:
            print("hmm, VNC viewer appears to have exited with result {}".format(res))
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
                if ans == 'q':
                    break

                elif ans in ('h', '?'):
                    print(menu)

                elif ans == 'a':
                    print(self.totp.now())

                elif ans == 'r':
                    self.rdconfig(self.config_path)

                elif ans == 'c':
                    self.connect()

                elif ans == 'x':
                    self.disconnect()

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
