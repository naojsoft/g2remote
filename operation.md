# Instructions for Use

This assumes that you have already installed the g2remote package with
all requirements as outlined in the file [install.md](https://github.com/naojsoft/g2remote/blob/master/install.md).

## One-time setup instructions

1). Generate an ssh-key with

```bash
$ ssh-keygen -b 4096 -f gen2_connect
```
      
(or using the key generation program supplied with your ssh client).
This should generate *two* (2) files: `gen2_connect` and
`gen2_connect.pub`. Email your designated contact at Subaru with the
`gen2_connect.pub` file and your full name, institution and assigned
remote observation periods. 

NOTE: you only need to do this once--if you have remote observed
(generating a key) before, simply mention this in the email and do
not generate or attach a new key (unless we ask you to!).
    
## Per-observation setup instructions

2). You should receive from Subaru a `config.yml` file and a
    `g2vncpasswd` file.  It is recommended to keep these together in the
    same folder.  

Examine the `config.yml` file, and make sure that the values for the
following keys are correct:  
* `vnc_passwd_file`: the path to the g2vncpasswd file sent to you
* `ssh-key`: the path to the *non*-".pub" file generated in step 1) of the
           one-time setup instructions.
      
If any of these are incorrect, correct them using a text editor.

3). Start *two* (2) command shells, each one with your Python environment
    enabled where you installed `g2remote`.
    
4). In the first shell, run 

```bash
$ g2connect -f config.yml
```
  
If all parameters are correct in the config file, you will be
prompted to enter a 2-factor authentication code.

5). In the second shell, run *another*

```bash
$ g2connect -f config.yml
```
  
Use the "a" command to show the 2-factor authentication code.  You
will likely need to *type* the code into the other command shell (cut
and paste does not seem to work on some platforms).
 
The 2FA code changes every minute or so--if you wait too long to
type the code, you may need to use the "a" command again as
necessary to get another code.  (If the connection times
out before you can get the code entered, just initiate another
connection and try again).

6). Once you are connected in the first shell, you can pop up the Gen2
    displays from the second shell by typing the number of the screen
    (1-8).  See the explanation below for a description of the screens.
    
7). When you are ready to terminate the observation, close the VNC
    windows and then type the "q" command in the second shell.  Type
    Ctrl-C in the first shell to terminate the tunneled connection.

## Notes

* You can use virtual desktops to position the screens if you don't
  have many displays.

* If you have additional hosts with displays, you can also start
  additional instances of `g2connect` on those hosts (you will need 2
  terminals on each host, as described above) and use them to pop up
  additional screens on those hosts.

## Screens

| Screen | Content |
| ------ | ------- |
| 1      | hskymon (observation planning tool) |
| 2      | instrument control GUIs |
| 3      | integgui2 (observation execution tool) |
| 4      | fitsview (QDAS, quick look, slit alignment, etc), HSC obslog |
| 5      | guideview (guiding control and monitoring) |
| 6      | statmon (current telescope status) |
| 7      | instrument control and monitoring GUIs |
| 8      | instrument control and monitoring GUIs |

Note that each screen is a 2550x1380 VNC window, so you will be managing a
lot of large screens. Probably you are not interested in all screens.
Consult your Support Astronomer to decide which ones are important for
your observation.

