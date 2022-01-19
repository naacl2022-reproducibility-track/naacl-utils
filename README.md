# NAACL Utils

A command line tool to help authors submit Docker images to the [NAACL Reproducibility Track](https://naacl2022-reproducibility-track.github.io/).

*Requires [Docker](https://www.docker.com/) and Python 3.7 or newer.* If you don't have a suitable Python installation, see [Installing Python](#installing-python) below.

Instructions for using the tool should be kept in [the Dockerization tutorial](https://github.com/naacl2022-reproducibility-track/naacl2022-reproducibility-track.github.io/blob/main/_tutorial/04_submitting.md).
Information relevant to developers of the tool should be kept in this Readme.

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
