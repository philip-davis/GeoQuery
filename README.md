# GeoQuery

GeoQuery is a library for accessing geospatial imagery across mutliple repositories using a single API. GeoQuery is an ancillary interface library as part of the [FIRE-D ML framework](https://github.com/philip-davis/ML-FIRE-D).

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
geo.Query(target="sentinel^instrument=sar,product=slc", lon1, lat1, lon2, lat2, sdate, edate, projection, resolution)
```

The `target` argument to query is a string that tells the GeoInterface which repository to query. The part before the carot (`sentinel` in this case) is a reference to the name assigned in `AddAdapter()`. The comma separated list of key/value pairs after the carot are adapter-specific arguments.

Other arguments to `GeoInterface.Query()` (all required):
* `lon1`, `lat1`: The lower-left corner of the geographic area being requested
* `lon2`, `lat2`: the upper-right corner of the geographic area being requested
* `sdate`: the start date of the temporal range being queried. This should be a string formatted as `YYYYMMDD`, although GeoQuery makes a best effort to interpret differently-formatted arguments for dates.
* `edate`: the end date of the temporal range being queried
* `projection`: a string containing an [EPSG](https://en.wikipedia.org/wiki/EPSG_Geodetic_Parameter_Dataset) projection, e.g. `EPSG:32610`
* `resolution`: per-pixel resolution, in meters

The arguments together imply a two-dimensional grid: a pair of geographic coordinates on a projection define a rectangle (disregarding elevation), and that rectangle can be overlaid with a grid with an average spacing of `resolution`. The variance and regularity of this spacing will depend on the appropriateness of the chosen projection. `GeoInterface.Query()` returns one or more [ND-arrays](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html) as a Python dictionary. Most geospatial respositories provide multiple quantities in their raw data; each will have its own grid of the same dimensions. The query handles this by returning an array over the same grid for each quantity, and organizing these into a dictionary with the keys being the repository-provided quantity names.

## Adapters
We provide two example adapters, one for accessing [HLS](https://hls.gsfc.nasa.gov) data from the [EarthData](https://www.earthdata.nasa.gov) repository, and another for accessing [Sentinel](https://sentinels.copernicus.eu/web/sentinel/missions/sentinel-1) data from the [Copernicus SciHub](https://scihub.copernicus.eu). 

### Sentinel
The Sentinel adaptor is provided by objects of the `SentinelAdapter` class. There are no arguments to this class.

To use the Sentinel adaptor, it is necessary to have a user credentials with SciHub. This can be created by following the [user guide instructions](https://scihub.copernicus.eu/userguide/SelfRegistration). These credentials should be placed in the following environment variables before running a Query:

* `DS_SENTINEL_USERNAME`: the username on SciHub
* `DS_SENTINEL_PWD`: the password for SciHub

### HLS
To use the HLS adapter, a data provider must be prepared. This data provider can either be [downloaded](https://search.earthdata.nasa.gov/search?q=HLS%20Daily%20Global) into a local directory or a remote [OSF](https://osf.io/) repository. The data should be organized within the data provider in a two-layer directory structure according to the first two coordinates in its MGRS tile coordinate. An example of this organization can be seen in the [geoquery_labels](https://osf.io/v4uz9/) provider. A utility `file_earthdata.py` is provided to perform this organization automatically on a local directory. The usage of this utility is:

`file_earthdata.py <source_dir> <target_dir>`

where **source_dir** is a directory containing geotiff files downloaded from EarthData in a flat structure, and **target_dir** is the directroy into which the two-layer structure will be built. For example,

`file_earthdata.py ~/Downloads/hls_data ./earthdata`

will result in a directory structure being built in the `earthdata` folder, into which is copied all the geotiff files in `~/Downloads/hls_data` that have the naming structure used by EarthData.

The HLS adapter is provied by objects of the `EarthDataAdapter` class. Two arguments can be passed when creating an `EarthDataAdapter()` object:

* `directory`: the location of the data. The interpretation of this is provider-specific. For a `local` provider, the directory is where the two-layer directory structure can be found (typically the value of **target_dir** used with the `file_earthdata.py` utility.
* `provider`: the provider type to be used. Possible values are `local`, which indicates the raw geospatial imagery can be found on a local file, or 'osf', which indicates the data can be found in an OSF repository. Default is `local`.

## Target Modifiers
The target parameter of `GeoInterface.Query()` is semantically significant, starting with an adapter name followed by a carot, followed by a comma-separted list of `<key>=<value>` modifiers. These modifiers are adapter-specific.

### Sentinel Adapter Modifiers:
  * `instrument`: A valid short name for a Sentinel-1 instrument, currently only supports `SAR`
  * `product`: A valid product type for Sentinel-1, for example `SLC`

### EarthData Adapter Modifiers:
There are currently no modifieres implemented for the EarthData adapter.

Example:
`python3 multisource_test.py -121.827 46.805 -121.6255 46.92621 20230228 20230301 EPSG:32610 30`

To use EarthData, `get_mgrs_idx.py` should be run to create the MGRS tile offset database file.

Earthdata should be organized in a directory structure with a top-level directory of grid zone and bottom-level directory of 100km tile. For example, the datasets for 10TES should be in <earthdata directory>/10T/ES/ 

###
