from typing import Optional

import click
from click_help_colors import HelpColorsCommand, HelpColorsGroup

from .version import VERSION

# TODO: Change these to NAACL-specific org and cluster.
BEAKER_ORG = "AI2"
BEAKER_CLUSTER = "AI2/petew-cpu"


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


@main.command(
    cls=HelpColorsCommand,
    help_options_color="green",
    help_headers_color="yellow",
    context_settings={"max_content_width": 115},
)
def setup():
    """
    One-time setup.
    """
    from beaker import Beaker, Config, ConfigurationError

    # Beaker setup.
    try:
        beaker = Beaker.from_env()
    except ConfigurationError:
        # Tell user to create Beaker account and get user token.
        click.echo(
            f"Please go to {click.style('https://beaker.org', fg='yellow')} and create an account.\n"
            f"Once you've done that, copy your user token from {click.style('https://beaker.org/user', fg='yellow')} and enter it below."
        )
        beaker_token = click.prompt("User token", type=str)

        # Create and save Beaker config.
        config = Config(user_token=beaker_token, default_org=BEAKER_ORG)
        beaker = Beaker(config)
        beaker.config.default_workspace = f"{BEAKER_ORG}/{beaker.user}"
        beaker.config.save()

    click.secho("\N{check mark} Setup complete", fg="green")


@main.command(
    cls=HelpColorsCommand,
    help_options_color="green",
    help_headers_color="yellow",
    context_settings={"max_content_width": 115},
)
@click.argument("image", type=str)
@click.argument("name", type=str)
def submit(image: str, name: str):
    """
    Submit a Docker image for your experiment to https://beaker.org.

    E.g.

        naacl-utils submit hello-world run-1

    """
    from beaker import Beaker, ImageNotFound

    beaker = Beaker.from_env()
    beaker.config.default_org = BEAKER_ORG
    beaker.config.default_workspace = f"{BEAKER_ORG}/{beaker.user}"

    # Check if image exists on Beaker and create it if it doesn't.
    beaker_image = image.replace(":", "-")
    try:
        image_data = beaker.get_image(f"{beaker.user}/{beaker_image}")
    except ImageNotFound:
        image_data = beaker.create_image(
            name=beaker_image,
            image_tag=image,
        )

    # Submit experiment.
    experiment_data = beaker.create_experiment(
        name,
        {
            "version": "v2-alpha",
            "tasks": [
                {
                    "name": "main",
                    "image": {"beaker": image_data["id"]},
                    "context": {"cluster": BEAKER_CLUSTER},
                    "result": {"path": "/unused"},  # required even if the task produces no output.
                },
            ],
        },
    )
    experiment_id = experiment_data["id"]
    click.echo(
        f"Experiment {click.style(experiment_id, fg='blue')} submitted.\n"
        f"See progress at https://beaker.org/ex/{experiment_id}"
    )


if __name__ == "__main__":
    main()
