# stactools-noaa-climate-normals

[![PyPI](https://img.shields.io/pypi/v/stactools-noaa-climate-normals)](https://pypi.org/project/stactools-noaa-climate-normals/)

- Name: noaa-climate-normals
- Package: `stactools.noaa_climate_normals`
- [stactools-noaa-climate-normals on PyPI](https://pypi.org/project/stactools-noaa-climate-normals/)
- Owner: @pjhartzell
- [Dataset homepage](https://www.ncei.noaa.gov/products/land-based-station/us-climate-normals)
- STAC extensions used:
  - [item-assets](https://github.com/stac-extensions/item-assets)
  - [proj](https://github.com/stac-extensions/projection/)
  - [raster](https://github.com/stac-extensions/raster)
  - [scientific](https://github.com/stac-extensions/scientific)
  - [table](https://github.com/stac-extensions/table)
- Extra fields:
  - `noaa_climate_normals:period`: Climate normal time period, e.g., 1981-2010 or 1991-2020.
  - `noaa_climate_normals:frequency`: Climate normal temporal interval (frequency), e.g., daily or hourly.
  - `noaa-climate_normals:time_index`: Time step index, e.g., month of year (1-12).
- [Browse the example in human-readable form](https://radiantearth.github.io/stac-browser/#/external/raw.githubusercontent.com/stactools-packages/noaa-climate-normals/main/examples/catalog.json)

## Background

The NOAA U.S. Climate Normals provide information about typical climate conditions for thousands of weather station locations across the United States. Normals act both as a ruler to compare current weather and as a predictor of conditions in the near future. Climate normals are calculated for uniform time periods (conventionally 30 years long), and consist of annual/seasonal, monthly, daily, and hourly averages and statistics of temperature, precipitation, and other climatological variables for each weather station.

Data is available in two forms: tabular and gridded. The tabular data consists of weather variables for each weather station location. The gridded data is an interpolated form of the tabular data and is derived from the [NClimGrid](https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=gov.noaa.ncdc:C00332) dataset. Gridded data is limited to temperature and precipitation information.

Three Collections, and corresponding Items, can be generated with this package:

1. noaa-climate-normals-tabular

    - Items for each Climate Normal time period and temporal interval combination, e.g. monthly data for the 1991-2020 time period.
    - Each Item contains a single GeoParquet asset created from the weather variables for all available weather stations (~10-15K) for the particular time period and frequency combination. The source data for each weather station is contained in a unique CSV file, so a single GeoParquet asset contains data from 10-15K CSV files.

2. noaa-climate-normals-gridded

    - Items for each timestep in each Climate Normal time period and temporal interval combination, e.g., month 1 (January) of the monthly data in the 1991-2020 time period.
    - Each Item contains COG Assets for all available weather variables.

3. noaa-climate-normals-netcdf

    - Items for the NetCDF files that serve as the source data for the COGs in the `noaa-climate-normals-gridded` Collection.

## STAC Examples

- Collections

    - [tabular](examples/noaa-climate-normals-tabular/collection.json)
    - [gridded](examples/noaa-climate-normals-gridded/collection.json)
    - [netcdf](examples/noaa-climate-normals-netcdf/collection.json)

- Items

    - [tabular](examples/noaa-climate-normals-tabular/1981_2010-daily/1981_2010-daily.json)
    - [gridded](examples/noaa-climate-normals-gridded/1991_2020-monthly-01/1991_2020-monthly-01.json)
    - [netcdf](examples/noaa-climate-normals-netcdf/prcp-1991_2020-monthly-normals-v1.0/prcp-1991_2020-monthly-normals-v1.0.json)

The example Collections and Items in the `examples` directory can be created by running `./scripts/create_examples.py`.

## Installation

```shell
pip install stactools-noaa-climate-normals
```

## Command-line Usage

To create a Collection:

```shell
stac noaa-climate-normals <gridded|netcdf|tabular> create-collection
```

To create an Item, e.g., for the `monthly` tabular data from the `1991-2020` time period:

```shell
stac noaa-climate-normals tabular create-item <filepath to text file of csv hrefs> monthly 1991-2020 <item and geoparquet destination directory>
```

Each Collection has unique subcommands and options. Use `stac noaa-climate-normals --help` to explore subcommands and options.

## Contributing

We use [pre-commit](https://pre-commit.com/) to check any changes.
To set up your development environment:

```shell
pip install -e .
pip install -r requirements-dev.txt
pre-commit install
```

To check all files:

```shell
pre-commit run --all-files
```

To run the tests:

```shell
pytest -vv
```
