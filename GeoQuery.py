from geojson import Polygon
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
import mgrs
from osgeo import gdal,ogr,osr
from datetime import date
from zipfile import ZipFile
import numpy as np
import pickle
import sys
import os

def GetSRCoord(lon, lat, projection):
    source = osr.SpatialReference()
    source.ImportFromEPSG(4326)

    target = osr.SpatialReference()
    if projection.startswith("EPSG"):
        ignored, epsg = projection.split(":")
        target.ImportFromEPSG(int(epsg))
    else:
        raise ValueError(f"unsupported projection: {projection}")

    transform = osr.CoordinateTransformation(source, target)
    point = ogr.CreateGeometryFromWkt(f"POINT ({lat} {lon})")
    point.Transform(transform)

    ignored, xcoord, ycoord = str(point).split(' ')
    xcoord = xcoord.replace('(','')
    ycoord = ycoord.replace(')','')
    return((float(xcoord), float(ycoord)))

class EarthDataBoxQuery:
    def __init__(self, target, lon1, lat1, lon2, lat2, sdate, edate):
        m = mgrs.MGRS()
        tl = m.toMGRS(max(lat1, lat2), min(lon1, lon2), MGRSPrecision = 0)
        lr = m.toMGRS(min(lat1, lat2), max(lon1, lon2), MGRSPrecision = 0)
        self.tl = (tl[:-2], tl[-2:])
        self.lr = (lr[:-2], lr[-2:])
        
        

class SentinelBoxQuery:
    def __init__(self, api, target, lon1, lat1, lon2, lat2, sdate, edate):
        self.api = api
        box = Polygon([[(lon1, lat1), (lon2, lat1), (lon2, lat2), (lon1, lat2), (lon1, lat1)]])
        self.footprint = geojson_to_wkt(box)
        self.date = (sdate, edate)
        self.args = {}
        try:
            ignored, argpart = target.split('^')
            args = argpart.split(',')
            for arg in args:
                key, value = arg.split('=')
                self.args[key] = value
        except ValueError:
            pass

    def GetProductList(self):
        self.products = self.api.query(self.footprint, date=self.date, producttype=self.args['product'], instrumentshortname=self.args['instrument'])
        return(self.products)

class EarthDataAdapter:
    def __init__(self, directory):
        self.dir = directory
    
    def CreateQuery(self, target, lon1, lat1, lon2, lat2, sdate, edate):
        return(EarthDataBoxQuery(target, lon1, lat1, lon2, lat2, sdate, edate))

class SentinelAdapter:
    def __init__(self):
        username = os.getenv('DS_SENTINEL_USERNAME')
        password = os.getenv('DS_SENTINEL_PWD')
        self.api = SentinelAPI(username, password, 'https://apihub.copernicus.eu/apihub')
        try:
            with open(".sentineldb", "rb") as file:
                self.db = pickle.load(file)
        except FileNotFoundError:
            self.db = {}
    def __del__(self):
        with open(".sentineldb", "wb") as file:
            pickle.dump(self.db, file)

    def CreateQuery(self, target, lon1, lat1, lon2, lat2, sdate, edate):
        return(SentinelBoxQuery(self.api, target, lon1, lat1, lon2, lat2, sdate, edate))

    def GetProducts(self, products):
        download_prod = {}
        for product in products:
            if product not in self.db:
                download_prod[product] = products[product]
        self.api.download_all(download_prod)
        for product in download_prod:
            self.db[product] = {"product": download_prod[product], "projections": {}}
            zipf = download_prod[product]['title']
            with ZipFile(f'{zipf}.zip', 'r') as zip_ref:
                zip_ref.extractall(zipf)
            measure_dir = f'{zipf}/{zipf}.SAFE/measurement/'
            self.db[product]['measurements'] = [measure_dir+x for x in os.listdir(measure_dir)]

    def ProjectMeasurement(self, measurement, projection, resolution):
        root_ext = os.path.splitext(measurement)
        proj_file = f'{root_ext[0]}_{projection}_{resolution}_{root_ext[1]}'
        gdal.Warp(proj_file, measurement, dstSRS = projection, xRes = resolution, yRes = resolution)
        return(proj_file)

    def GetSubset(self, product, band, polarity, projection, lb, ub, resolution):
        proj_file = self.db[product]['projections'][(band, polarity, projection, resolution)]
        print(proj_file)
        if self.db[product]['product']['orbitdirection'] == 'ASCENDING':
            xres = resolution
            yres = resolution
        else:
            xres = -resolution
            yres = -resolution
        tl = (min(lb[0], ub[0]), max(lb[1], ub[1]) + resolution)
        dat = gdal.Open(proj_file)
        geo = dat.GetGeoTransform()
        print(f'geo: {geo}, tl: {tl}')
        ret_offset = [0, 0]
        size = [int(abs(ub[0] - lb[0]) / resolution), int(abs(ub[1] - lb[1]) / resolution)]
        offset = [int((tl[0] - geo[0]) / xres), int((tl[1] - geo[3]) / yres)]
        if offset[0] < 0:
            size[0] = size[0] + offset[0]
            ret_offset[0] = -offset[0]
            offset[0] = 0
        if offset[1] < 0:
            size[1] = size[1] + offset[1]
            ret_offset[1] = -offset[1]
            offset[1] = 0
        print(f'offset: {offset}')
        if (offset[0] + size[0]) > dat.RasterXSize:
            size[0] = dat.GetXSize() - offset[0]
        if (offset[1] + size[1]) > dat.RasterYSize:
            size[1] = dat.GetYSize() - offset[1]

        print(f'size: {size}')
        if size[0] > 0 and size[1] > 0:
            arr = dat.ReadAsArray(xoff = offset[0], yoff = offset[1], xsize = size[0], ysize = size[1])
        else:
            arr = None
        return arr, ret_offset

    def GetBandPolarity(self, filename):
        fattrs = os.path.basename(filename).split('-')
        return((fattrs[3], fattrs[1]))

    def BuildResult(self, products, lon1, lat1, lon2, lat2, projection, resolution):
        lb = GetSRCoord(lon1, lat1, projection)
        ub = GetSRCoord(lon2, lat2, projection)
        print(f'lb: {lb}, ub: {ub}')
        width = int(abs(lb[0] - ub[0]) / resolution)
        height = int(abs(lb[1] - ub[1]) / resolution)
        results = {}
        for product in products:
            for measurement in self.db[product]['measurements']:
                (band, polarity) = self.GetBandPolarity(measurement)
                if (band, polarity, projection, resolution) not in self.db[product]['projections']:
                    self.db[product]['projections'][(band, polarity, projection, resolution)] = self.ProjectMeasurement(measurement, projection, resolution)
                subset, offset = self.GetSubset(product, band, polarity, projection, lb, ub, resolution) 
                if not subset is None:
                    if not (band, polarity) in results:
                        results[(band, polarity)] = np.ndarray((height, width), dtype=subset.dtype)
                        results[(band, polarity)].fill(np.nan)
                    results[(band, polarity)][offset[1]:offset[1]+subset.shape[0], offset[0]:offset[0]+subset.shape[1]] = subset 

class GeoInterface:
    def __init__(self):
        self.adapters = {}
    def AddAdapter(self, name, adapter):
        self.adapters[name] = adapter
    def CreateQuery(self, adapter, target, lon1, lat1, lon2, lat2, sdate, edate):
        return(adapter.CreateQuery(target, lon1, lat1, lon2, lat2, sdate, edate))
    def Query(self, target, lon1, lat1, lon2, lat2, sdate, edate, projection, resolution):
        adapter = self.FindAdapter(target)
        query = self.CreateQuery(adapter, target, lon1, lat1, lon2, lat2, sdate, edate)
        products = query.GetProductList()
        adapter.GetProducts(products)
        return(adapter.BuildResult(products, lon1, lat1, lon2, lat2, projection, resolution))

    def FindAdapter(self, target):
        try:
            name, ignored = target.split('^')
        except ValueError:
            name = target
        return(self.adapters[name])

if __name__ == "__main__":
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
    hls = EarthDataAdapter('earthdata')
    geo.AddAdapter("sentinel1", sentinel)
    geo.AddAdapter("hls", hls)

    geo.Query("sentinel1^instrument=sar,product=slc", lon1, lat1, lon2, lat2, sdate, edate, projection, res)
    #geo.Query('hls', lon1, lat1, lon2, lat2, sdate, edate, projection, res)
    sentinel = None
    geo = None         


