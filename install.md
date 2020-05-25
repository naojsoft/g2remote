# Requirements

## All platforms

* Large monitor or monitors, capable of displaying 2550x1380 windows
  (e.g. Apple Retina display).  Otherwise you will be scrolling A LOT.
  You can use virtual desktops with one or two large screens.
* Working command line with ssh client
* Ability to generate strong ssh keys (e.g. `ssh-keygen` program;
  usually already installed with ssh client)
* python (version 3.5 or higher) in which you can install your own
  packages (e.g. Miniconda or Anaconda)
* `g2remote` download (this package)

## Linux

* tigervnc viewer client program (version 1.7.1 or higher recommended,
  usually in the "tigervnc-viewer" package)
* `vncpasswd` program (usually found in the "tigervnc-common" package)

## MacOSX

* "Screen Sharing" program.  Usually comes installed with the OS

## Windows

* VNC viewer client program can be either TightVNC or RealVNC.
* Windows 10 has OpenSSH built in, but you might need to enable it. Go to:

  Settings->Apps->Optional features

  Make sure that OpenSSH is in the list. If not, use the "Add a feature"
  button to add OpenSSH to the list of "Optional features".

# Installation

Activate your Python 3.5+ environment and do

```bash
$ python setup.py install
```

to install `g2remote`.  This should download and install any missing
Python requirements.


## Operation

See file [operation.md](https://github.com/naojsoft/g2remote/blob/master/operation.md)


## Downloads

* Windows users:
  * Download the version compatible with your Windows OS version (usually 64-bit version).
  * You can download and install TightVNC or RealVNC from the following locations
    (choose one or the other - you don't need both):
  * [TightVNC download page](https://www.tightvnc.com/download.php)
  * [RealVNC Viewer download page](https://www.realvnc.com/en/connect/download/viewer/)
  * For TightVNC, we recommend that you install only the "Viewer" component.
    In the TightVNC installer's "Choose Setup Type" screen, select the "Custom" option.
    Then, in the "Custom Setup" screen, click on the "TightVNC Server" dropdown menu and select
    "Extra feature will be unavailable". The "TightVNC Server" dropdown menu should change to a red "X".

* All users: make sure you have a working Python 3.5 or later standard
  environment.  (We recommend installing Miniconda if you are not sure;
  [download here](https://docs.conda.io/en/latest/miniconda.html))


