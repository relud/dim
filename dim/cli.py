import logging
from datetime import timedelta

import click

from dim.app import run_check
from dim.error import DateRangeException, DimConfigError
from dim.models.dim_config import DimConfig
from dim.utils import read_config

SOURCE_PROJECT = "data-monitoring-dev"
INPUT_DATE_FORMAT = "%Y-%m-%d"


logging.basicConfig(level=logging.INFO)


def validate_date_range(start_date, end_date):
    if start_date > end_date:
        raise DateRangeException("Start date must be older than end date.")

    return start_date, end_date


def validate_config(config_path):
    """
    Validates dim config. Ensures it can ve loaded correctly
    and that it fullfils all requirements.
    """

    logging.info("Validating config: %s" % config_path)

    try:
        DimConfig(**read_config(config_path=config_path)["dim_config"])
    except (KeyError, TypeError) as _err:
        raise DimConfigError(_err)

    logging.info("Config appears to be validl: %s" % config_path)


@click.group()
def cli():
    pass


@cli.command()
@click.option("--project", required=False, type=str, default=SOURCE_PROJECT)
@click.option("--dataset", required=True, type=str)
@click.option(
    "--table", required=True, type=str
)  # required for now until we add
# support for grabbing all configs in a dataset
@click.option(
    "--date_partition_parameter",
    required=True,
    type=click.DateTime(formats=[INPUT_DATE_FORMAT]),
)  # rename date_partition_parameter to something shorter,
# required until we add support for full tables
def run(project: str, dataset: str, table: str, date_partition_parameter: str):
    run_check(project, dataset, table, date_partition_parameter)


@cli.command()
@click.option("--project", required=False, type=str, default=SOURCE_PROJECT)
@click.option("--dataset", required=True, type=str)
@click.option(
    "--table", required=True, type=str
)  # required for now until we add support
# for grabbing all configs in a dataset
@click.option(
    "--start_date",
    required=True,
    type=click.DateTime(formats=[INPUT_DATE_FORMAT]),
)
@click.option(
    "--end_date",
    required=True,
    type=click.DateTime(formats=[INPUT_DATE_FORMAT]),
)
def backfill(project, dataset, table, start_date, end_date):
    """
    Cmd to trigger tests execution for the specified table
    for the specified date range.
    """

    validate_date_range(start_date, end_date)

    logging.info(
        "Running dim backfill checks on %s:%s.%s for date range: %s - %s"
        % (project, dataset, table, start_date, end_date)
    )

    date = start_date
    while date <= end_date:
        run_check(project, dataset, table, date)
        date += timedelta(days=1)

    logging.info(
        "Dim backfill completed for %s:%s.%s for date range: %s - %s"
        % (project, dataset, table, start_date, end_date)
    )


@cli.command()
@click.argument("config_path")  # , type=click.Path(file_okay=False))
def validate(config_path):
    """
    Cmd used to valide a dim yaml config. Ensures the yaml file
    can be loaded correctly and that it fullfils all requirements.
    """

    validate_config(config_path)
