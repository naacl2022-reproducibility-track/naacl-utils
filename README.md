# NAACL Utils

A command line tool to help authors submit Docker images to the [NAACL Reproducibility Track](https://naacl2022-reproducibility-track.github.io/).

*Requires [Docker](https://www.docker.com/) and Python 3.7 or newer.* If you don't have a suitable Python installation, see [Installing Python](#installing-python) below.

## Prerequisites

Please follow these carefully before doing anything else.

1. Create an account on [Beaker.org](https://beaker.org). You can sign up either with GitHub or your email, both are fine.
1. Find and copy your Beaker username at [beaker.org/user](https://beaker.org/user) under the "User Details" section.
1. Open a new [Beaker add request](https://github.com/naacl2022-reproducibility-track/naacl-utils/issues/new?assignees=epwalsh&labels=beaker&template=beaker_permissions.md&title=Please+add+me+to+the+NAACL+Beaker+organization) issue and fill in all of the information that it asks you for, including your Beaker username. This will notify a NAACL reviewer that they need to add you to the NAACL organization on Beaker.
1. Wait for a NAACL reviewer to close the issue with confirmation that they've added you to the Beaker organization.
1. Then proceed to [install and configure naacl-utils](#installing-and-configuring-naacl-utils).

After completing these steps, you are ready to [submit a Docker image](#submitting-a-docker-image) for review.

## Installing and configuring naacl-utils

Before attempting to install **naacl-utils**, make sure you have Python 3.7 or newer installed on your machine.
You can check this by running `python --version` or `python3 --version`. If both of those commands return an error or display a version that's older than 3.7, see [Installing Python](#installing-python) below.

Once you have a suitable Python installation on your machine, you can install **naacl-utils** directly with [pip](https://github.com/pypa/pip):

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

The first argument to `naacl-utils submit` is the name of your Docker image (e.g. "nvidia/cuda:11.0-base"), and the second is an arbitrary unique name you assign to your submission ("cuda-test-run-1").
If you make another submission you'll have to use a different name.

The `--cmd` parameter is optional. You can use this to override the `CMD` of your Docker image. Similarly there is also the `--entrypoint` parameter for overriding the `ENTRYPOINT` of your image.

If the submission was successful it will print out a link on Beaker.org that you can follow to track the progress of your submission and view the logs.
If the run fails for some reason you can use the logs to debug it and then resubmit when you're ready.

## Installing Python

**naacl-utils** requires Python 3.7 or newer. If you don't already have a suitable Python installation on your machine, the easiest way to get one is with [Miniconda](https://docs.conda.io/en/latest/miniconda.html).

Miniconda is straight-forward to install on MacOS, Linux, and Windows.
On MacOS, for example, you can install Miniconda via [Homebrew](https://brew.sh/):

```bash
brew install miniconda
```

Otherwise just use the official [installer links](https://docs.conda.io/en/latest/miniconda.html#latest-miniconda-installer-links).

Once you have Miniconda installed, you can create and activate a new Python 3.7 virtual environment by running:

```bash
conda create -n naacl python=3.7
conda activate naacl
```
