# NAACL Utils

A command line tool to help authors submit Docker images to the [NAACL Reproducibility Track](https://naacl2022-reproducibility-track.github.io/).

*Requires [Docker](https://www.docker.com/) and Python 3.7 or newer.*

## Setup

### Prerequisites

#### Create a [Beaker](https://beaker.org) account

The very first thing you'll need to do is create an account on [Beaker.org](https://beaker.org). Then you'll need to provide your username to a NAACL reviewer so that they can add you to the NAACL organization on Beaker.
Once you've received confirmation that you've been granted access to the NAACL organization, you can proceed to [install and configure naacl-utils](#installing-and-configuring-naacl-utils).

#### Installing Python

**naacl-utils** requires Python 3.7 or newer. If you don't already have a suitable Python installation on your machine, the easiest way to get one is with [Miniconda](https://docs.conda.io/en/latest/miniconda.html).

Miniconda is straight-forward to install on Mac, Linux, and Windows.
On Mac OSX, for example, you can install Miniconda via [Homebrew](https://brew.sh/):

```bash
brew install miniconda
```

Otherwise just use the official [installer links](https://docs.conda.io/en/latest/miniconda.html#latest-miniconda-installer-links).

Once you have Miniconda installed, you can create and activate a new Python 3.7 virtual environment by running:

```bash
conda create -n naacl python=3.7
conda activate naacl
```

### Installing and configuring naacl-utils

You can install **naacl-utils** directly with [pip](https://github.com/pypa/pip):

```bash
pip install naacl-utils
```

After the installation completes, you'll need to run the `setup` command once to configure **naacl-utils**:

```
naacl-utils setup
```

Then follow the prompts to complete the setup.

## Submitting a Docker image

You can submit a new Docker image with the `naacl-utils submit` command. For example:

```bash
docker pull nvidia/cuda:11.0-base
naacl-utils submit nvidia/cuda:11.0-base cuda-test-run-1 --cmd nvidia-smi
```
