# GeoQuery

GeoQuery is a library for accessing geospatial imagery across mutliple repositories using a single API.

## Prerequisites
GeoQuery depends on the osgeo module, which is part of the [GDAL](https://gdal.org) package. Installing the gdal package requires pre-installing the gdal binaries on most platforms. Binaries are available for [download](https://gdal.org/download.html#binaries) for many different platforms, as well as source code.

### Installing GDAL on MacOS
If the brew package manager is avaialable, install GDAL using the command `brew install gdal`  

### Installing GDAL on Ubuntu
Install GDAL using `sudo apt-get install gdal-bin`

## Installation
From the repository root direction, run:

`pip install .`

## Usage
To use GeoQuery, import the GeoInterface class, as well as any desired adapters, e.g.
`from geoquery import GeoInterface, SentinelAdapter, EarthDataAdapter`

Each geoimagery repository requires an adaptor that knows how to translate spatiotemporal requests into repository-specific queries, and collate/reproject/resample the data as requested. These adaptors must be loaded into the GeoInterface for later usage, and assigned a name for later reference. For example:

```
geo = GeoInterface()
geo.AddAdapter("sentinel", SentinelAdapter())
```

Adds an adapter for accessing the Sentinel data repository from ESA. This repository can later be targeted in queries using the assigned name:
```
geo.Query("sentinel^instrument=sar,product=slc", lon1, lat1, lon2, lat2, sdate, edate, projection, resolution)
```

The first argument to query is a string that tells the GeoInterface which repository to query. The part before the carot (`sentinel` in this case) is a reference to the name assigned in `AddAdapter()`. The comma separated list of key/value pairs after the carot are adapter-specific arguments.

Other arguments to `GeoInterface.Query()` (all required):
* `lon1`, `lat1`: The lower-left corner of the geographic area being requested
* `lon2`, `lat2`: the upper-right corner of the geographic area being requested
* `sdate`: the start date of the temporal range being queried. This should be a string formatted as `YYYYMMDD`, although GeoQuery makes a best effort to interpret differently-formatted arguments for dates.
* `edate`: the end date of the temporal range being queried
* `projection`: a string containing an [EPSG](https://en.wikipedia.org/wiki/EPSG_Geodetic_Parameter_Dataset) projection, e.g. `EPSG:32610`
* `resolution`: per-pixel resolution, in meters



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
