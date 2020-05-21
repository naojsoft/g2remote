# Instructions for Use

This assumes that you have already installed the g2remote package with
all requirements as outlined in the file [install.md](https://github.com/naojsoft/g2remote/blob/master/install.md).

## One-time setup instructions

1). Generate an ssh-key with

```bash
$ ssh-keygen -b 4096 -f gen2_connect
```

IMPORTANT: *do not add a passphrase*; the program will not work with a key
that has a passphrase.
      
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
      
If any of these are incorrect, or you are instructed to modify them,
correct them using a text editor.

3). Start a command shell with the Python environment where you installed
    `g2remote`.
    
4). In the shell, run 

```bash
$ g2connect -f config.yml
```

You should be prompted with a `g2connect>` command loop.

5). Run the command "c" to connect.  If successful, it should just return
    to the command prompt.

```bash
g2connect> c
connecting ...
g2connect> 
```

6). Open VNC screens by typing the number of the screen (1-8).  See the
    explanation below for a description of the screens.
    
7). When you are ready to terminate the observation, close the VNC
    windows and then type the "q" command.

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

