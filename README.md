# GeoQuery

Copernicus login and password need to be set in environment variables:

`DS_SENTINEL_USERNAME`
`DS_SENTINEL_PWD`

Example:
`python3 GeoQuery.py -121.827 46.805 -121.6255 46.92621 20230228 20230301 EPSG:32610 30`

To use EarthData, `get_mgrs_idx.py` should be run to create the MGRS tile offset database file.

Earthdata should be organized in a directory structure with a top-level directory of grid zone and bottom-level directory of 100km tile. For example, the datasets for 10TES should be in <earthdata directory>/10T/ES/ 
