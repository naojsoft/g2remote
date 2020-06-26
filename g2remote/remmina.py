import os
import base64
import configparser

from Crypto.Cipher import DES3


remmina_template = """
[remmina]
password={password}
name={name}
protocol=VNC
sound=off
server=localhost:{port}
colordepth=24
viewmode=1
cert_ignore=0
console=0
ssh_enabled=0
ssh_auth=0
sharesmartcard=0
quality=0
ssh_loopback=0
relax-order-checks=0
microphone=0
gateway_usage=0
disableautoreconnect=0
disablepasswordstoring=0
glyph-cache=0
shareprinter=0
disableclipboard=0
showcursor=0
viewonly=1
disableencryption=0
disableserverinput=0
window_width=2440
window_height=1406
window_maximize=0
"""


def encode_remmina_vnc_password(secret, pwd):
    import base64
    from Crypto.Cipher import DES3
    # pad password to multiple of 8 with nulls
    n = 8 - len(pwd) % 8
    pwd = pwd + '\x00' * n
    res = DES3.new(secret[:24], DES3.MODE_CBC, secret[24:]).encrypt(pwd)
    res = base64.encodebytes(res).decode()
    return res

def get_remmina_secret(filepath):
    if not os.path.exists(filepath):
        return None
    config = configparser.ConfigParser()
    config.read(filepath)

    secret = config.get('remmina_pref', 'secret')
    secret = base64.decodebytes(secret.encode())
    return secret

def write_remmina_config_file(filepath, secret, num, config):
    d = dict(password=encode_remmina_vnc_password(secret,
                                                  config['vnc_passwd']),
             name="Gen2 Screen {}".format(num), port=5900 + num)

    with open(filepath, 'w') as out_f:
        out_f.write(remmina_template.format(**d))

def write_gen2_screens(screens, config):
    dir1 = os.path.join(os.environ['HOME'], ".remmina")
    dir2 = os.path.join(os.environ['HOME'], ".config", "remmina")

    rem_dir = dir2
    if os.path.isdir(dir1):
        rem_dir = dir1

    prefpath = os.path.join(rem_dir, "remmina.pref")
    secret = get_remmina_secret(prefpath)
    if secret is None:
        raise ValueError("Could not find remmina secret")

    for num in screens:
        filepath = os.path.join(rem_dir, "gen2_s{}.remmina".format(num))
        write_remmina_config_file(filepath, secret, num, config)
        print("wrote {}".format(filepath))
