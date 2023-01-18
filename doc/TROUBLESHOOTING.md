# TROUBLESHOOTING

Q: I'm getting the error:

> Unknown exception: p must be exactly 1024, 2048, or 3072 bits long

A: This error is normally shown when your key is not inserted on the
   Subaru side.  See the FAQ about testing during your proscribed test
   time range.

---

Q: I sometimes get this error:

> paramiko.ssh_exception.BadAuthenticationType: Bad authentication
> type; allowed types: ['keyboard-interactive']

A: This is a known issue.  You can ignore it at the present and just
   retry your command.

---

Q: I get the following warning:

> UserWarning: Unknown ssh-ed25519 host key for 128.171.203.222: xxxxxx
> key.get_name(), hostname, hexlify(key.get_fingerprint())

A: This may happen the first time you connect only.  But we have
   reports of it happening more than once for some users.  In any
   case, it does not indicate that the connection failed.

---

Q: I am getting the following error:

> paramiko.ssh_exception.NoValidConnectionsError: [Errno None] Unable to connect to port NN on W.X.Y.Z

A: this usually occurs when too many failed attempts to connect have
   occurred in a row.  The server will deny connection attempts for
   10 minutes from the same account.

---

Q: I am getting the following error:

>  NameError: name 'platform_system' is not defined

A: We have reports of this error on Windows systems.  Try the following
after activating your Miniconda environment which you used to install
g2remote.

> pip install --upgrade pip
> pip install --upgrade setuptools
> cd .../g2remote
> git clean -xdf
> python setup.py install

---

Q: The displays are updating slowly. Is there anything I can do?

A: The update rate depends for the most part on the quality of the internet
connection between you and the observatory location at the summit of Mauna
Kea.

*Only open as many screens as you need*.  For most observers, this is
about 3-4 screens or so.  Your Support Astronomer or Operator can advise
you on which screens are most important for your observation.

For screens that contain displays of simple web pages like Maunakea
Weather center, web cams, etc. it is more effective to just open your
own web browser to connect to those pages.

---

Q: I can't control anything. Is this normal?

A: Yes. At the moment, Gen2 extended remote is view only. We may
   allow control of some windows eventually after suitable safety
   measures are in put in place to prevent the unexpected movement of
   the telescope, damage to instruments or data and software of Gen2.

