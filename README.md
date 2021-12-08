# NAACL Utils

A command-line interface to help authors submit to the [NAACL Reproducibility Track](https://naacl2022-reproducibility-track.github.io/).

## Setup

**naacl-utils** requires [Docker](https://www.docker.com/) and Python 3.7 or newer.
The easiest way to create suitable Python environment on your machine is with [Miniconda](https://docs.conda.io/en/latest/miniconda.html),
which is straight-forward to install on Mac, Linux, and Windows.

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

Then install **naacl-utils** with:

```bash
pip install naacl-utils
```

Now you can run the `setup` command with:

```
naacl-utils setup
```

Follow the prompts to complete your setup.

## Submitting a Docker image

Once you've completed the setup above, you can submit a new Docker image with the `naacl-utils submit` command.

For example:

```bash
docker pull hello-world
naacl-utils submit hello-world run-1
```
