import os
from typing import Any, Dict, List, Optional

import fsspec
import numpy as np
import rasterio
import rasterio.shutil
import xarray
from pystac import Asset, MediaType
from pystac.utils import make_absolute_href
from rasterio.io import MemoryFile

from . import constants
from .utils import item_id

TRANSFORM = [0.04166667, 0.0, -124.70833333, 0.0, -0.04166667, 49.37500127]

GTIFF_PROFILE = {
    "crs": "epsg:4326",
    "width": 1385,
    "height": 596,
    "dtype": "float32",
    "count": 1,
    "transform": rasterio.Affine(*TRANSFORM),
    "driver": "GTiff",
}

COG_PROFILE = {"compress": "deflate", "blocksize": 512, "driver": "COG"}


def create_cogs(
    nc_href: str,
    frequency: constants.Frequency,
    period: constants.Period,
    cog_dir: str,
    cogs: Dict[str, Any],
    time_index: Optional[int] = None,
    cog_hrefs: Optional[List[str]] = None,
) -> None:
    """Creates COGs for all variables in a NetCDF for a particular Climate
    Normal frequency.

    Args:
        nc_href (str): HREF to to the NetCDF file.
        period (constants.Period): Climate normal time period of CSV data, e.g.,
            '1991-2020'.
        frequency (constants.Frequency): Temporal interval of COGs to be
            created, e.g., 'monthly' or 'daily'.
        cog_dir (str): Directory to store created COGs.
        cogs (Dict[str, Any]): A dictionary for COG metadata to be used in STAC
            Item assets.
        time_index (Optional[int]): 1-based time index into the NetCDF
            timestack, e.g., 'time_index=3' for the month of March for a NetCDF
            holding monthly frequency data.
        cog_hrefs (Optional[List[str]]): List of HREFs to existing COGs. New
            COGs will not be created if they exist in the list.
            holding monthly frequency data.
    """
    if cog_hrefs:
        existing_cog_filenames = {os.path.basename(href): href for href in cog_hrefs}
    with fsspec.open(nc_href, mode="rb"):
        with xarray.open_dataset(nc_href) as dataset:
            data_vars = list(dataset.data_vars)
            latitudes = dataset.lat.values
            if frequency is not constants.Frequency.DAILY:
                data_vars = [var for var in data_vars if frequency.name.lower() in var]

            if time_index:
                kwargs = {constants.TIME_VARS[frequency]: time_index - 1}
                id = item_id(frequency, period, time_index)
            else:
                kwargs = None
                id = item_id(frequency, period, 1)

            for data_var in data_vars:
                if "dly" in data_var:
                    generic_data_var = data_var.replace("dly", "")
                elif "mly" in data_var:
                    generic_data_var = data_var.replace("mly", "")
                elif "seas" in data_var:
                    generic_data_var = data_var.replace("seas", "")
                elif "ann" in data_var:
                    generic_data_var = data_var.replace("ann", "")
                else:
                    generic_data_var = data_var

                cog_filename = f"{id}-{generic_data_var}.tif"

                cogs[generic_data_var] = {}
                cogs[generic_data_var]["description"] = dataset[data_var].long_name
                cogs[generic_data_var]["unit"] = dataset[data_var].units

                if cog_hrefs and cog_filename in existing_cog_filenames:
                    cogs[generic_data_var]["href"] = existing_cog_filenames[
                        cog_filename
                    ]
                else:
                    cogs[generic_data_var]["href"] = os.path.join(cog_dir, cog_filename)

                    nodata = 0 if "flag" in data_var else np.nan

                    if kwargs:
                        values = dataset[data_var].isel(**kwargs)
                    else:
                        values = dataset[data_var]

                    # round per comments in NetCDF files
                    if "prcp" in data_var:
                        values = np.round(values, 2)
                    else:
                        values = np.round(values, 1)

                    if latitudes[0] < latitudes[-1]:
                        values = np.flipud(values)

                    with MemoryFile() as mem:
                        with mem.open(**GTIFF_PROFILE, nodata=nodata) as temp:
                            temp.write(values, 1)
                            rasterio.shutil.copy(
                                temp, cogs[generic_data_var]["href"], **COG_PROFILE
                            )


def cog_asset(data_var: str, cog: Dict[str, str]) -> Asset:
    """Creates a STAC Asset for a COG.

    Args:
        data_var (str): Name of the NetCDF data variable the COG was created
            from.
        cog (Dict[str, str]): Dictionary of COG metadata.

    Returns:
        Asset: A STAC Asset for the COG.
    """
    nodata = 0 if "flag" in data_var else "nan"

    unit = cog["unit"].replace("_", " ")
    if "number of" in unit:
        unit = unit.replace("number of ", "")

    raster_bands = [
        {
            "data_type": "float32",
            "nodata": nodata,
            "unit": unit,
            "spatial_resolution": 5000,
        }
    ]

    return Asset(
        href=make_absolute_href(cog["href"]),
        description=cog["description"],
        media_type=MediaType.COG,
        roles=["data"],
        extra_fields={"raster:bands": raster_bands},
    )
