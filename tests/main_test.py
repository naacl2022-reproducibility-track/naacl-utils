import subprocess

from naacl_utils.version import VERSION


def test_version():
    result = subprocess.run(["naacl-utils", "--version"], capture_output=True, text=True)
    assert result.returncode == 0
    assert VERSION in result.stdout
