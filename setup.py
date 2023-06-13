from setuptools import setup

setup(
   name='geoquery',
   version='0.1',
   description='Query geospatial imagery',
   author='Philip Davis',
   author_email='philip.davis@sci.utah.edu',
   packages=['geoquery'],
   install_requires=['wheel', 'osfclient', 'geojson', 'sentinelsat', 'mgrs', 'gdal', 'numpy'],
)
