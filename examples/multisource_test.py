import sys
from geoquery import GeoInterface, SentinelAdapter, EarthDataAdapter

lon1 = float(sys.argv[1])
lat1 = float(sys.argv[2])
lon2 = float(sys.argv[3])
lat2 = float(sys.argv[4])
sdate = sys.argv[5]
edate = sys.argv[6]
projection = sys.argv[7]
res = float(sys.argv[8])
geo = GeoInterface()
sentinel = SentinelAdapter()
hls = EarthDataAdapter('v4uz9', provider='osf')
geo.AddAdapter("sentinel1", sentinel)
geo.AddAdapter("hls", hls)

sentinel_result = geo.Query("sentinel1^instrument=sar,product=slc", lon1, lat1, lon2, lat2, sdate, edate, projection, res)
hls_result = geo.Query('hls', lon1, lat1, lon2, lat2, sdate, edate, projection, res)

