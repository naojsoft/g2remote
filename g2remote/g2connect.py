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
import sys
import os
import platform
import subprocess
import yaml
import time

screens = [0, 1, 2, 3, 4, 5, 6, 7, 8]
menu = """
Choose one of the following options:
c: connect
a: show 2-factor authentication code
h: show this help message
q: quit
r: re-read config file
N: (digit from 1-8): open screen N
"""

config = None

def rdconfig(path):
    global config

    print("reading config file...")
    with open(path, 'r') as in_f:
        config = yaml.safe_load(in_f)

def connect(proc):
    global config

    # TEMP: until we can figure out how to get keyboard input to ssh
    # running in a subprocess
    print("After connecting, start another instance of g2connect\n"
          "in another terminal to open displays.\n\n""")

    args = ['ssh', '-p', str(config['port']), '-N', '-T', '-x', '-a']
    for num in screens:
        args.append('-L')
        args.append('{}:localhost:{}'.format(5900 + num, 5900 + num))

    ssh_key = config.get('ssh_key', None)
    if ssh_key is not None:
        args.extend(['-i', ssh_key])

    args.append('{}@{}'.format(config['user'], config['server']))

    print("making ssh connection...")
    cmd_str = ' '.join(args)
    res = os.system(cmd_str)

def disconnect(proc):
    print("disconnecting...")
    for k, p in list(proc.items()):
        del proc[k]
        p.kill()

def display(proc, num):
    global config

    print("attempting to start VNC sessions...")
    system = platform.system().lower()

    if system == 'linux':
        vncpwd = config['vnc_passwd_file']
        args = ['vncviewer', '-passwd', vncpwd, 'localhost:{}'.format(num)]

    elif system == 'darwin':
        # <-- Mac OS X
        user = config['user']
        passwd = config['vnc_passwd']
        port = 5900 + num
        args = ['open', '-n', '-g',
                "vnc://{}:{}@localhost:{}".format(user, passwd, port)]

    elif system == 'windows':
        vncpwd = config['vnc_passwd_file']
        args = ['vncviewer', '-passwd', vncpwd, 'localhost:{}'.format(num)]

    procname = 'screen_{}'.format(num)

    proc[procname] = subprocess.Popen(args, stdin=subprocess.PIPE,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)

    time.sleep(1)
    res = proc[procname].poll()
    if res is not None and res != 0:
        print("hmm, VNC viewer appears to have exited with result {}".format(res))
        print("stdout:\n" + proc['tunnel'].stdout.read().decode())
        print("stderr:\n" + proc['tunnel'].stderr.read().decode())


def cmd_loop(proc):
    global config

    digits = ["{}".format(num) for num in screens]
    print(menu)

    while True:
        sys.stdout.write("g2connect> ")
        sys.stdout.flush()
        ans = sys.stdin.readline().strip()

        try:
            if ans == 'q':
                return

            elif ans in ('h', '?'):
                print(menu)

            elif ans == 'a':
                import pyotp
                totp = pyotp.TOTP(config['secret'])
                print(totp.now())

            elif ans == 'r':
                rdconfig(options.config)

            elif ans == 'c':
                connect(proc)

            elif ans == 'x':
                disconnect(proc)

            elif ans in digits:
                display(proc, int(ans))

            else:
                print("I don't know that command. Type 'h' for a menu.")

        except KeyboardInterrupt:
            print("Caught keyboard interrupt!")
            return

        except Exception as e:
            print("Exception running command: {}".format(e))
            # TODO: traceback


def main(options, args):

    if options.config is None or not os.path.exists(options.config):
        print("Please specify location of config file with -f")
        sys.exit(1)

    rdconfig(options.config)

    proc = dict()

    try:
        cmd_loop(proc)

    except KeyboardInterrupt:
        print("detected keyboard interrupt!")

    for p in proc.values():
        p.wait()
