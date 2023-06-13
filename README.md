# GeoQuery

GeoQuery is a library for accessing geospatial imagery across mutliple repositories using a single API.

## Prerequesites
GeoQuery depends on the osgeo module, which is part of the [GDAL](https://gdal.org) package. Installing the gdal package requires pre-installing the gdal binaries on most platforms. Binaries are available for [download](https://gdal.org/download.html#binaries) for many different platforms, as well as source code.

### Installing GDAL on MacOS
If the brew package manager is avaialable, install GDAL using the command `brew install gdal`  

### Installing GDAL on Ubuntu
Install GDAL using `sudo apt-get install gdal-bin`

## Installation
From the repository root direction, run:

`pip install .`

## Usage

## Adapters

### Sentinel
Copernicus login and password need to be set in environment variables:

`DS_SENTINEL_USERNAME`
`DS_SENTINEL_PWD`

Example:
`python3 GeoQuery.py -121.827 46.805 -121.6255 46.92621 20230228 20230301 EPSG:32610 30`

To use EarthData, `get_mgrs_idx.py` should be run to create the MGRS tile offset database file.

Earthdata should be organized in a directory structure with a top-level directory of grid zone and bottom-level directory of 100km tile. For example, the datasets for 10TES should be in <earthdata directory>/10T/ES/ 

###
