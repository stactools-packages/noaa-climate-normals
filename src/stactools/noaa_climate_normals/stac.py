import logging

from pystac import Item, Collection
from pystac.extensions.projection import ProjectionExtension

logger = logging.getLogger(__name__)


def create_collection(source: str) -> Collection:
    """Create a STAC Collection

    Args:
        source (str): The directory containing the Climate Normals data

    Returns:
        Collection: STAC Collection object
    """
    raise NotImplementedError


def create_item(asset_href: str) -> Item:
    """Create a STAC Item

    This function should include logic to extract all relevant metadata from an
    asset, metadata asset, and/or a constants.py file.

    See `Item<https://pystac.readthedocs.io/en/latest/api.html#item>`_.

    Args:
        asset_href (str): The HREF pointing to an asset associated with the item

    Returns:
        Item: STAC Item object
    """
    raise NotImplementedError
