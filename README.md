# GeoQuery

`__main__` is hard-coded to query Sentinel1 SAR SLC data. Additional sources in progress.

Copernicus login and password need to be set in environment variables:

`DS_SENTINEL_USERNAME`
`DS_SENTINEL_PWD`

Example:
`python3 GeoQuery.py -121.827 46.805 -121.6255 46.92621 20230228 20230301 EPSG:32610 30`
