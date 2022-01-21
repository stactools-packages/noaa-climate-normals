import logging

import click

from stactools.noaa_climate_normals import stac

logger = logging.getLogger(__name__)


def create_noaaclimatenormals_command(cli):
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
    @click.argument("destination")
    def create_collection_command(destination: str):
        """Creates a STAC Collection

        Args:
            destination (str): An HREF for the Collection JSON
        """
        collection = stac.create_collection()

        collection.set_self_href(destination)

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
