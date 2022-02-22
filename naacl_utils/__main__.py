import sys
import uuid
from typing import Optional

import click
import packaging.version
import requests
from beaker import Beaker, ConfigurationError, ExperimentConflict, ImageNotFound
from click.parser import split_arg_string
from click_help_colors import HelpColorsCommand, HelpColorsGroup
from requests.exceptions import HTTPError

from .version import VERSION

BEAKER_ORG = "NAACL"
BEAKER_CLUSTER = "NAACL/server"
BEAKER_ADDRESS = "https://beaker.org"


def get_beaker_client(token: Optional[str] = None) -> Beaker:
    if token is not None:
        beaker = Beaker.from_env(user_token=token)
    else:
        beaker = Beaker.from_env()
    beaker.config.agent_address = BEAKER_ADDRESS
    beaker.config.default_org = BEAKER_ORG
    beaker.config.default_workspace = f"{BEAKER_ORG}/{beaker.user}"
    return beaker


def check_beaker_permissions(beaker: Beaker):
    assert beaker.config.default_workspace is not None
    try:
        # This will fail with a 403 if user doesn't have access to the NAACL organization.
        beaker.ensure_workspace(beaker.config.default_workspace)
    except HTTPError as exc:
        if exc.response.status_code == 403:
            raise click.ClickException(
                "Unable to access NAACL organization on Beaker. Did you complete all of the steps here?\n"
                + click.style(
                    "https://github.com/naacl2022-reproducibility-track/naacl-utils#prerequisites",
                    fg="yellow",
                )
                + "\n\nIf so, and you're still seeing this error, please submit a bug report here:\n"
                + click.style(
                    "https://github.com/naacl2022-reproducibility-track/naacl-utils/issues/new",
                    fg="yellow",
                ),
            )


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
    type=click.Choice(["debug", "info", "warning", "error"], case_sensitive=False),
    show_choices=True,
)
def main(log_level: Optional[str] = None):
    """
    A command-line interface to help authors submit to the NAACL Reproducibility Track.
    """
    if log_level is not None:
        import logging

        logging.basicConfig(level=getattr(logging, log_level.upper()))

    # Ensure that we're running the latest version.
    try:
        response = requests.get(
            "https://api.github.com/repos/naacl2022-reproducibility-track/naacl-utils/releases/latest",
            timeout=1,
        )
        response.raise_for_status()
        latest_version = packaging.version.parse(response.json()["tag_name"])
        if latest_version > packaging.version.parse(VERSION):
            click.secho(
                f"You're using naacl-utils version {VERSION}, but there is a newer version available ({latest_version}).\n"
                "Please upgrade with: 'pip install --upgrade naacl-utils'",
                fg="yellow",
                err=True,
            )
    except HTTPError:
        pass


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
        click.echo(
            f"Please go to {click.style('https://beaker.org', fg='yellow')} and create an account.\n"
            f"Once you've done that, copy your user token from {click.style('https://beaker.org/user', fg='yellow')} and enter it below."
        )
        beaker_token = click.prompt("User token", type=str)

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

    click.echo(
        click.style("\N{check mark} Setup complete, you are authenticated as ", fg="green")
        + click.style(f"'{beaker.user}'", fg="green", bold=True)
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
        raise click.ClickException(
            "Beaker client not properly configured, did you forget to run the 'naacl-utils setup' command?",
        )

    check_beaker_permissions(beaker)

    beaker_image = image.replace(":", "-").replace("/", "-") + "-" + str(uuid.uuid4())[:4]
    try:
        # Make sure an image with this name doesn't exist on Beaker.
        # It's unlikely because we add a random sequence of characters to the end of the name,
        # but possible.
        image_data = beaker.get_image(f"{beaker.user}/{beaker_image}")
        # If it does exist, we'll delete it.
        beaker.delete_image(image_data["id"])
    except ImageNotFound:
        pass

    # (Re-)create image.
    image_data = beaker.create_image(
        name=beaker_image,
        image_tag=image,
    )

    # Submit experiment.
    try:
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
        raise click.ClickException(
            f"A run with the name '{click.style(run_name, fg='red')}' already exists, try using a different name.",
        )
    experiment_id = experiment_data["id"]
    click.echo(
        f"Experiment {click.style(experiment_id, fg='blue')} submitted.\n"
        f"See progress at https://beaker.org/ex/{experiment_id}"
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
        raise click.ClickException(
            "Beaker client not properly configured, did you forget to run the 'naacl-utils setup' command?",
        )

    check_beaker_permissions(beaker)

    exp_id: str
    experiments = beaker.list_experiments()
    for experiment in experiments:
        if experiment["name"] == run_name or experiment["fullName"] == run_name:
            exp_id = experiment["id"]
            break
    else:
        raise click.ClickException(
            f"Could not find a run with the name '{click.style(run_name, fg='red')}'. Are you sure that's the correct name?"
        )
    logs = "".join((chunk.decode() for chunk in beaker.get_logs_for_experiment(exp_id)))

    # Beaker adds the date and time to log lines, so we remove those first.
    log_lines = [line[line.find(" ") + 1 :] for line in logs.split("\n")]
    logs = "\n".join(log_lines)

    with expected_output_file:
        expected_output = expected_output_file.read()

    if expected_output in logs:
        click.echo(click.style("\N{check mark} Results successfully verified", fg="green"))
    else:
        raise click.ClickException(
            "Expected output not found in logs.\n"
            "You can see the logs at " + click.style(f"https://beaker.org/ex/{exp_id}", fg="yellow")
        )


if __name__ == "__main__":
    main()
