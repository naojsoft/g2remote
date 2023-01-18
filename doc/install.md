# Requirements

## All platforms

* High-resolution monitor or monitors, capable of displaying largish
  windows; HiDPI screens such as used in Apple Retina displays work well.
* Working command line with an ssh client
* Ability to generate strong ssh keys (e.g. `ssh-keygen` program;
  usually already installed with ssh client)
* python (version 3.7 or higher) in which you can install your own
  packages (we recommend using Miniconda or Anaconda)
* HTML5 enabled web browser.  Supported browsers include Firefox, Chrome,
  Safari and Edge.  Others may work as well.

## Windows (additional)

* Windows 10 has OpenSSH built in, but you might need to enable it. Go to:

  Settings->Apps->Optional features

  Make sure that OpenSSH is in the list. If not, use the "Add a feature"
  button to add OpenSSH to the list of "Optional features".

# Installation

Create a separate conda environment with a version of Python >= 3.7.
This will insure that you don't disturb any other Python environments
you may have configured.  Here we give it the name "subaru-gers":

```bash
$ conda create -n subaru-gers python=3.10
```

Conda activate your Python 3.7+ environment.  Install the "git" and
"paramiko" packages:

```bash
$ conda activate subaru-gers
(subaru-gers)$ conda install git paramiko
```

Now install g2remote like this:

```bash
(subaru-gers)$ pip install git+https://github.com/naojsoft/g2remote
```

This should download and install g2remote as well as any missing
Python requirements.  *We recommend to install paramiko by conda, as shown
above, because some platforms have trouble building/using the pip installed
version*.


## Operation

See file [operation.md](https://github.com/naojsoft/g2remote/blob/master/doc/operation.md)


## Downloads

* All users: make sure you have a working Python 3.7 or later standard
  environment.  (We recommend installing Miniconda if you are not sure;
  [download here](https://docs.conda.io/en/latest/miniconda.html))


