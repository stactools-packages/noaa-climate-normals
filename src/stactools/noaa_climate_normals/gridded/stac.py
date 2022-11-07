import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import stactools.core.create
from pystac import Collection, Item, Link, MediaType, Summaries
from pystac.extensions.item_assets import AssetDefinition, ItemAssetsExtension
from stactools.core.io import ReadHrefModifier

from ..constants import LANDING_PAGE_LINK, LICENSE_LINK, PROVIDERS
from ..netcdf.utils import netcdf_item_id
from ..utils import modify_href
from . import constants
from .cog import cog_asset, create_cogs
from .utils import item_title, load_item_assets, nc_href_dict

logger = logging.getLogger(__name__)


def create_item(
    nc_href: str,
    frequency: constants.Frequency,
    time_index: int,
    cog_dir: str,
    *,
    api_url_netcdf: Optional[str] = None,
    cog_hrefs: Optional[List[str]] = None,
    read_href_modifier: Optional[ReadHrefModifier] = None,
) -> Item:
    """Creates a STAC Item and COGs for a single timestep of Climate Normal
    data, e.g., an Item for the month of March for the monthly Climate Normals.

    Args:
        nc_href (str): HREF to one of the NetCDF files containing data required
            for Item creation. Any additional required NetCDF files are assumed
            to exist in the same location.
        frequency (Frequency): Temporal interval of Item to be created, e.g.,
            'daily', 'monthly', or 'seasonal'.
        time_index (int): 1-based time index into the NetCDF timestack, e.g.,
            'time_index=3' for the month of March for a NetCDF.
        cog_dir (str): Directory to store created COGs.
        api_url_netcdf (str): Base STAC API URL for NetCDF Items from which the
            COGs are derived, .e.g., "https://planetarycomputer.microsoft.com/
            "api/stac/v1/collections/noaa-climate-normals-netcdf/items/". The
            Item IDs of the NetCDF files used to create the COGs for this Item
            will be appended to the base STAC API URL and used to create a
            "derived_from" Link for each source NetCDF file.
        cog_hrefs (Optional[List[str]]): List of HREFs to existing COGs. New
            COGs will not be created if they exist in the list.
            holding monthly frequency data.
        read_href_modifier (Optional[ReadHrefModifier]): An optional function

    Returns:
        Item: A STAC Item for a single timestep of Climate Normal data.
    """
    period = constants.Period(os.path.basename(nc_href).split("-")[1].replace("_", "-"))
    id = f"{period.value.replace('-', '_')}-{frequency}"

    if frequency is constants.Frequency.ANN:
        logger.info("time_index value is not used for Annual frequency data")
        time_index_ = None
    else:
        id += f"-{time_index}"
        time_index_ = time_index

    title = item_title(frequency, period, time_index_)

    cogs: Dict[str, Any] = {}
    nc_hrefs = nc_href_dict(nc_href, frequency)
    for nc_href in nc_hrefs.values():
        modified_nc_href = modify_href(nc_href, read_href_modifier)
        create_cogs(
            modified_nc_href, frequency, period, cog_dir, cogs, time_index_, cog_hrefs
        )

    item = stactools.core.create.item(next(iter(cogs.values()))["href"])
    item.id = id
    item.datetime = None
    item.common_metadata.start_datetime = datetime(
        int(period.value[0:4]), 1, 1, 0, 0, 0
    )
    item.common_metadata.end_datetime = datetime(int(period.value[5:]), 12, 31, 0, 0, 0)
    item.common_metadata.created = datetime.now(tz=timezone.utc)
    item.properties["noaa-climate-normals:frequency"] = frequency
    item.properties["noaa-climate-normals:period"] = period
    if time_index_:
        item.properties["noaa-climate-normals:time_index"] = time_index_
    item.properties["title"] = title

    item.assets.pop("data")
    for key, value in cogs.items():
        item.add_asset(key, cog_asset(key, value))

    if api_url_netcdf:
        for nc_href in nc_hrefs.values():
            href = os.path.join(api_url_netcdf, netcdf_item_id(nc_href))
            item.add_link(
                Link(
                    rel="derived_from",
                    target=href,
                    media_type=MediaType.JSON,
                    title="Source NetCDF File from NOAA NCEI",
                )
            )

    item.stac_extensions.append(constants.RASTER_EXTENSION_V11)

    return item


def create_collection() -> Collection:
    collection = Collection(**constants.COLLECTION)

    collection.providers = PROVIDERS

    collection.add_links(
        [LANDING_PAGE_LINK, LICENSE_LINK, constants.README, constants.DOCUMENTATION]
    )

    collection.summaries = Summaries(
        {
            "frequency": [f.value for f in constants.Frequency],
            "period": [p.value for p in constants.Period],
        }
    )

    item_asset_dicts = load_item_assets()
    for key, value in item_asset_dicts.items():
        item_asset_dicts[key] = AssetDefinition(value)
    item_assets = ItemAssetsExtension.ext(collection, add_if_missing=True)
    item_assets.item_assets = item_asset_dicts

    collection.stac_extensions.append(constants.RASTER_EXTENSION_V11)

    return collection
