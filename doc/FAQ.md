# FAQ

Q: Where do I put the configuration files that are sent me?

A: We recommend creating a *new, empty folder* and put your private and
public keys (gen2_connect and gen2_connect.pub) in there.
When we send you the configuration files for your observation, put them
also in this folder.

You will normally want to operate g2remote out of this folder unless you
have modified the config file to change the paths (not recommended).
i.e. you should "cd" to this folder before running the g2connect command.

**Do not put the private key and configuration files in the source code
(git clone) folder for g2remote--use a separate folder**.
   
---

Q: When can I test my connection before observation?

A: Your key will be inserted by approximately 10:30 HST (5:30 JST,
20:30 UTC) on the starting day of your observation run.  You can test
anytime between then and 17:00 HST.  Normally, a test takes only a few
minutes following the instructions in the "operation" document.

***After testing, disconnect and consult with your support astronomer
or the Subaru operator about when to connect again for your observation***.

***If you don't test your connection before 17:00 HST on the night of
your observation, troubleshooting and help may be limited from the
observatory side.***

---

Q: I'm getting the error:

   Unknown exception: p must be exactly 1024, 2048, or 3072 bits long

A: This error is normally shown when your key is not inserted on the
Subaru side.  See the note above about testing during your
proscribed test time range.

---

Q: I sometimes get this error:

   paramiko.ssh_exception.BadAuthenticationType: Bad authentication
   type; allowed types: ['keyboard-interactive']

A: This is a known issue.  You can ignore it at the present and just
retry your command.

---

Q: I get the following warning:

   UserWarning: Unknown ssh-ed25519 host key for 128.171.203.222: xxxxxx
    key.get_name(), hostname, hexlify(key.get_fingerprint())

A: This may happen the first time you connect only.  But we have
reports of it happening more than once for some users.  In any
case, it does not indicate that the connection failed.

---

Q: I am getting the following error:

   paramiko.ssh_exception.NoValidConnectionsError: [Errno None] Unable to connect to port 22 on w.x.y.z

A: this usually occurs when too many failed attempts to connect have
occurred in a row.  The server will deny connection attempts for
10 minutes from the same account.  Try again in a few minutes.

---

Q: I can't control anything within the screens. Is this normal?

A: Yes. At the moment, Gen2 extended remote is view only. We may
allow control of some windows eventually after suitable safety
measures are in put in place to prevent the unexpected movement of
the telescope, damage to instruments or data and software of Gen2.

---

Q: Can I use g2connect with a VPN?

A: Yes, but it is not necessary.  g2connect uses encrypted tunnels using
your SSH key to do its work.
