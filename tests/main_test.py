import os
import subprocess
from pathlib import Path

import docker
import pytest
from beaker import Config
from click.testing import CliRunner

from naacl_utils.__main__ import main
from naacl_utils.version import VERSION

DOCKER_IMAGE_NAME = "nvidia/cuda:11.0-base"
DOCKER_AVAILABLE = True

try:
    docker.from_env().images.pull("hello-world")
except docker.errors.DockerException:
    DOCKER_AVAILABLE = False


@pytest.fixture(scope="function")
def run_dir(tmp_path: Path) -> Path:
    os.environ[Config.CONFIG_PATH_KEY] = str(tmp_path / "config.yml")
    return tmp_path


@pytest.fixture(scope="function")
def run_name() -> str:
    import uuid

    return "test-" + str(uuid.uuid4())[:8]


@pytest.fixture
def beaker_token() -> str:
    return os.environ["BEAKER_USER_TOKEN"]


@pytest.fixture
def docker_image() -> str:
    docker_client = docker.from_env()
    docker_client.images.pull(DOCKER_IMAGE_NAME)
    return DOCKER_IMAGE_NAME


def test_version(run_dir):
    result = subprocess.run(["naacl-utils", "--version"], capture_output=True, text=True)
    assert result.returncode == 0
    assert VERSION in result.stdout


def test_setup(run_dir, beaker_token):
    runner = CliRunner()
    result = runner.invoke(main, ["setup"], input=beaker_token)
    assert result.exception is None
    assert "Setup complete" in result.output


@pytest.mark.skipif(not DOCKER_AVAILABLE, reason="Docker required")
def test_setup_and_submit(run_dir, beaker_token, docker_image, run_name):
    runner = CliRunner()

    # setup
    result = runner.invoke(main, ["setup"], input=beaker_token)
    assert result.exception is None
    assert "Setup complete" in result.output

    # submit
    result = runner.invoke(main, ["submit", docker_image, run_name, "--cmd='nvidia-smi'"])
    assert result.exception is None
    assert "See progress at" in result.output


def test_submit_without_setup(run_dir, beaker_token):
    assert not (run_dir / "config.yml").is_file()
    runner = CliRunner()
    result = runner.invoke(main, ["submit", "hello-world", "run-1"], input=beaker_token)
    assert result.exception is not None
    assert "did you forget to run the 'naacl-utils setup' command" in result.output
