import os
import sys
import shutil

def get_tile(name):
    metadata = f.split('.')
    if metadata[-1] == 'tif' or metadata[-1] == 'tiff':
        tile = metadata[2][1:]
        return(tile[0:-2], tile[-2:])
    else:
        return(None, None)

def get_file_loc(basedir, outer, inner):
    odir = f'{basedir}/{outer}'
    if os.path.exists(odir):
        if not os.path.isdir(odir):
            raise FileExistsError(f'{odir} exists, but is not a directory!')
    else:
        os.mkdir(odir)
    idir = f'{odir}/{inner}'
    if os.path.exists(idir):
        if not os.path.isdir(idir):
            raise FileExistsError(f'{idir} exists, but is not a directory!')
    else:
        os.mkdir(idir)
    return(idir)

srcdir = sys.argv[1]
basedir = sys.argv[2]

files = os.listdir(srcdir)
for f in files:
    if not os.path.isdir(f):
        outer, inner = get_tile(f)
        if inner != None and outer != None:
                dst = get_file_loc(basedir, outer, inner)            
                print(f'Copying {f} to {dst}')
                shutil.copy(f'{srcdir}/{f}', dst)
