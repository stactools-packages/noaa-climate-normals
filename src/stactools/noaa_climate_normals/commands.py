import logging
import os.path

import click

from stactools.noaa_climate_normals import stac

logger = logging.getLogger(__name__)


def create_noaa_climate_normals_command(cli):
    """Creates the stactools-noaa-climate-normals command line utility."""

    @cli.group(
        "noaa-climate-normals",
        short_help=(
            "Commands for working with the NOAA Climate Normals dataset"),
    )
    def noaa_climate_normals():
        pass

    @noaa_climate_normals.command(
        "create-collection",
        short_help="Creates a STAC collection",
    )
    @click.argument("SOURCE")
    @click.argument("DESTINATION")
    def create_collection_command(source: str, destination: str):
        """Converts NOAA Climate Normals data to a parquet table, and creates a collection (with items) for that table.

        Args:
            source (str): The source directory containing climate normals data
            destination (str): The target href that will hold the STAC collection, items, and parquet table
        """
        collection = stac.create_collection(source)
        collection.set_self_href(os.path.join(destination, "collection.json"))
        collection.save_object()

        return None

    @noaa_climate_normals.command("create-item",
                                  short_help="Create a STAC item")
    @click.argument("source")
    @click.argument("destination")
    def create_item_command(source: str, destination: str):
        """Creates a STAC Item

        Args:
            source (str): HREF of the Asset associated with the Item
            destination (str): An HREF for the STAC Collection
        """
        item = stac.create_item(source)

        item.save_object(dest_href=destination)

        return None

    return noaa_climate_normals
