import difflib
import logging
import sys
import tempfile
import uuid
from typing import List, Optional

import click
import packaging.version
import requests
import rich
from beaker import (
    Beaker,
    ConfigurationError,
    ExperimentConflict,
    ExperimentNotFound,
    ImageNotFound,
)
from click.parser import split_arg_string
from click_help_colors import HelpColorsCommand, HelpColorsGroup
from requests.exceptions import HTTPError
from rich import print
from rich.highlighter import NullHighlighter
from rich.logging import RichHandler
from rich.padding import Padding
from rich.prompt import Prompt
from rich.syntax import Syntax

from .version import VERSION

BEAKER_ORG = "NAACL"
BEAKER_CLUSTER = "NAACL/server"
BEAKER_ADDRESS = "https://beaker.org"
BUG_REPORT_URL = "https://github.com/naacl2022-reproducibility-track/naacl-utils/issues/new?assignees=&labels=bug&template=bug_report.md&title="
TUTORIAL_URL = "https://naacl2022-reproducibility-track.github.io/tutorial/submitting"


logger = logging.getLogger("naacl_utils")
rich.get_console().highlighter = NullHighlighter()


class NaaclUtilsError(Exception):
    """
    Custom error we raise when we don't want to print a stacktrace.
    """


def excepthook(exctype, value, traceback):
    """
    Used to patch `sys.excepthook` in order to customize handling of uncaught exceptions.
    """
    # For interruptions, call the original exception handler.
    if issubclass(exctype, (KeyboardInterrupt,)):
        sys.__excepthook__(exctype, value, traceback)
    # Ignore `NaaclUtilsError` because we don't need a traceback for those.
    elif issubclass(exctype, (NaaclUtilsError,)):
        logger.error(
            "[red italic]%s[/]",
            value,
            extra={"markup": True},
        )
    else:
        logger.error(
            "[red italic]Uncaught exception:[/]",
            exc_info=(exctype, value, traceback),
            extra={"markup": True},
        )


sys.excepthook = excepthook


def get_beaker_client(token: Optional[str] = None) -> Beaker:
    logger.debug("Initializing beaker client")
    if token is not None:
        beaker = Beaker.from_env(user_token=token)
    else:
        beaker = Beaker.from_env()
    beaker.config.agent_address = BEAKER_ADDRESS
    beaker.config.default_org = BEAKER_ORG
    beaker.config.default_workspace = f"{BEAKER_ORG}/{beaker.user}"
    return beaker


def insert_link(link: str) -> str:
    return f"[underline blue][link={link}]{link}[/][/]"


def check_beaker_permissions(beaker: Beaker):
    logger.debug("Checking beaker permissions")
    assert beaker.config.default_workspace is not None
    try:
        # This will fail with a 403 if user doesn't have access to the NAACL organization.
        beaker.ensure_workspace(beaker.config.default_workspace)
    except HTTPError as exc:
        if exc.response.status_code == 403:
            raise NaaclUtilsError(
                "Unable to access NAACL organization on Beaker. Did you complete all of the steps?\n\n"
                f"  {insert_link(TUTORIAL_URL)}\n\n"
                "If so, and you're still seeing this error, please submit a bug report here:\n\n"
                f"  {insert_link(BUG_REPORT_URL)}"
            )


def validate_run_name(run_name: str):
    if not run_name.replace("-", "").isalnum():
        raise NaaclUtilsError(
            f"Invalid run name '{run_name}'. Names can only contain letters, digits, and dashes."
        )
    if len(run_name) > 100:
        raise NaaclUtilsError("Run name is too long!")


def validate_expected_output(expected_output_lines: List[str]):
    for line in expected_output_lines:
        if line:
            break
    else:
        raise NaaclUtilsError("Expected output file has no content")


@click.group(
    cls=HelpColorsGroup,
    help_options_color="green",
    help_headers_color="yellow",
    context_settings={"max_content_width": 115},
)
@click.version_option(version=VERSION)
@click.option(
    "--log-level",
    help="Set the global log level.",
    type=click.Choice(["debug", "info", "warning"], case_sensitive=False),
    default="warning",
    show_choices=True,
)
def main(log_level: str = "warning"):
    """
    A command-line interface to help authors submit to the NAACL Reproducibility Track.
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(tracebacks_suppress=[click], show_time=False)],
    )

    # Ensure that we're running the latest version.
    try:
        logger.debug("Checking that naacl-utils is up-to-date")
        response = requests.get(
            "https://api.github.com/repos/naacl2022-reproducibility-track/naacl-utils/releases/latest",
            timeout=1,
        )
        response.raise_for_status()
        latest_version = packaging.version.parse(response.json()["tag_name"])
        if latest_version > packaging.version.parse(VERSION):
            logger.warning(
                f"[yellow]You're using naacl-utils version {VERSION}, but there is a "
                f"newer version available ({latest_version}).\n"
                "Please upgrade with: 'pip install --upgrade naacl-utils'[/]",
                extra={"markup": True},
            )
        else:
            logger.debug("naacl-utils is up-to-date")
    except HTTPError:
        logger.debug("Request to GitHub API failed", exc_info=sys.exc_info())


@main.command(
    cls=HelpColorsCommand,
    help_options_color="green",
    help_headers_color="yellow",
    context_settings={"max_content_width": 115},
)
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="Force the setup steps again to overwrite existing configuration.",
)
def setup(force: bool = False):
    """
    One-time setup.
    """

    def setup_beaker() -> Beaker:
        # Tell user to create Beaker account and get user token.
        print(
            f"Please go to {insert_link('https://beaker.org')} and create an account.\n"
            f"Once you've done that, copy your user token from {insert_link('https://beaker.org/user')} and enter it below."
        )
        beaker_token = Prompt.ask("User token", password=True)

        # Create and save Beaker config.
        beaker = get_beaker_client(token=beaker_token)
        beaker.config.save()

        return beaker

    beaker: Beaker
    if force:
        beaker = setup_beaker()
    else:
        try:
            beaker = get_beaker_client()
        except ConfigurationError:
            beaker = setup_beaker()

    check_beaker_permissions(beaker)

    print(
        f"[green]\N{check mark} Setup complete, you are authenticated as [bold]'{beaker.user}'[/][/]"
    )


@main.command(
    cls=HelpColorsCommand,
    help_options_color="green",
    help_headers_color="yellow",
    context_settings={"max_content_width": 115},
)
@click.argument("image", type=str)
@click.argument("run_name", type=str)
@click.option(
    "--entrypoint",
    type=str,
    help="Override the ENTRYPOINT of the Docker image.",
)
@click.option(
    "--cmd",
    type=str,
    help="Override the CMD of the Docker image.",
)
def submit(image: str, run_name: str, entrypoint: Optional[str] = None, cmd: Optional[str] = None):
    """
    Submit a Docker image for your experiment to https://beaker.org.

    E.g.

        naacl-utils submit hello-world run-1

    """
    try:
        beaker = get_beaker_client()
    except ConfigurationError:
        raise NaaclUtilsError(
            "Beaker client not properly configured, did you forget to run the 'naacl-utils setup' command?",
        )

    validate_run_name(run_name)
    check_beaker_permissions(beaker)

    beaker_image = image.replace(":", "-").replace("/", "-") + "-" + str(uuid.uuid4())[:4]
    try:
        logger.debug("Checking if image already exists")
        # Make sure an image with this name doesn't exist on Beaker.
        # It's unlikely because we add a random sequence of characters to the end of the name,
        # but possible.
        image_data = beaker.get_image(f"{beaker.user}/{beaker_image}")
        # If it does exist, we'll delete it.
        logger.debug("Removing existing image")
        beaker.delete_image(image_data["id"])
    except ImageNotFound:
        pass

    # (Re-)create image.
    logger.debug("Creating image")
    image_data = beaker.create_image(
        name=beaker_image,
        image_tag=image,
    )

    # Submit experiment.
    try:
        logger.debug("Submitting experiment")
        experiment_data = beaker.create_experiment(
            run_name,
            {
                "version": "v2-alpha",
                "tasks": [
                    {
                        "name": "main",
                        "image": {"beaker": image_data["id"]},
                        "context": {"cluster": BEAKER_CLUSTER},
                        "result": {
                            "path": "/unused"
                        },  # required even if the task produces no output.
                        "command": None if entrypoint is None else split_arg_string(entrypoint),
                        "arguments": None if cmd is None else split_arg_string(cmd),
                        "resources": {
                            "gpuCount": 1,
                            "sharedMemory": "1GiB",
                        },
                    },
                ],
            },
        )
    except ExperimentConflict:
        raise NaaclUtilsError(
            f"A run with the name '{run_name}' already exists, try using a different name.",
        )
    experiment_id = experiment_data["id"]
    print(
        f"Experiment [blue]{experiment_id}[/] submitted.\n"
        f"See progress at {insert_link('https://beaker.org/ex/' + experiment_id)}"
    )


@main.command(
    cls=HelpColorsCommand,
    help_options_color="green",
    help_headers_color="yellow",
    context_settings={"max_content_width": 115},
)
@click.argument("run_name", type=str)
@click.argument("expected_output_file", type=click.File("r"), default=sys.stdin)
def verify(run_name: str, expected_output_file):
    """
    Verify the results of a run against the expected output.
    """
    try:
        beaker = get_beaker_client()
    except ConfigurationError:
        raise NaaclUtilsError(
            "Beaker client not properly configured, did you forget to run the 'naacl-utils setup' command?",
        )

    validate_run_name(run_name)
    check_beaker_permissions(beaker)

    # Find the right experiment.
    try:
        experiment = beaker.get_experiment(f"{beaker.user}/{run_name}")
    except ExperimentNotFound:
        raise NaaclUtilsError(
            f"Could not find a run with the name '{run_name}'. Are you sure that's the correct name?"
        )

    # Make sure the experiment finished successfully.
    if not experiment.get("jobs") or experiment["jobs"][0]["status"].get("exitCode") != 0:
        raise NaaclUtilsError("Can only verify submissions that have completed successfully.")

    exp_id: str = experiment["id"]

    # Download the logs.
    logs = "".join(
        (chunk.decode(errors="ignore") for chunk in beaker.get_logs_for_experiment(exp_id))
    )

    # Beaker adds the date and time to log lines, so we remove those first.
    log_lines = [line[line.find(" ") + 1 :].rstrip() for line in logs.split("\n")]
    logs = "\n".join(log_lines)

    with expected_output_file:
        expected_output_lines = [line.rstrip() for line in expected_output_file.readlines()]
        expected_output = "\n".join(expected_output_lines)

    # Make sure the expected output isn't empty or something.
    validate_expected_output(expected_output_lines)

    if expected_output in logs:
        # All good! Upload the expected output to Beaker datasets.
        print("[green]\N{check mark} Results successfully verified[/]")
        print("Uploading results...")
        with tempfile.NamedTemporaryFile(mode="w+t", suffix=".log") as tmpfile:
            tmpfile.write(expected_output)
            tmpfile.seek(0)
            beaker.create_dataset(run_name, tmpfile.name, target="out.log", force=True)
        print("[green]\N{check mark} Done![/]")
    else:
        # Print a diff if the logs aren't too long.
        if max(len(log_lines), len(expected_output_lines)) < 500:
            diff = Syntax(
                "\n".join(
                    list(
                        difflib.unified_diff(
                            log_lines, expected_output_lines, fromfile="Actual", tofile="Expected"
                        )
                    )
                ),
                "diff",
            )
            print(Padding(diff, 1))
            raise NaaclUtilsError("Expected output not found in logs.")
        else:
            # Otherwise just write the actual logs to a file so the user can inspect them further.
            log_file = tempfile.NamedTemporaryFile(mode="w+t", suffix=".log", delete=False)
            log_file.write(logs)
            raise NaaclUtilsError(
                f"Expected output not found in logs.\n"
                f"You can view the full logs here:\n[yellow]{log_file.name}[/]"
            )


if __name__ == "__main__":
    main()
