import mgrs
import pickle

m = mgrs.MGRS()

def char_range(c1, c2):
    """Generates the characters from `c1` to `c2`, inclusive."""
    for c in range(ord(c1), ord(c2)+1):
        yield chr(c)

tile_column = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
tile_row = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'U', 'V']

mgrs_idx = {}
for first in range(1, 61):
    for second in char_range('A', 'Z'):
        mgrs_idx[(first, second)] = {}
        tiles = []
        found_col = []
        found_row = []
        for third in tile_column:
            for fourth in tile_row:
                mgrs_str = f'{first}{second}{third}{fourth}'
                try:
                    latlon = m.toLatLon(mgrs_str)
                    tiles.append((third, fourth))
                    found_col.append(third)
                    found_row.append(fourth)
                except Exception:
                    pass 
        low_col = None
        low_row = None
        if not tiles:
            continue
        if 'Z' not in found_col:
            low_col = found_col[0]
        else:
            gap = False
            for col in tile_column:
                if col not in found_col:
                    gap = True
                else:
                    if gap:
                        low_col = col
                        break
        if 'Z' not in found_row:
            low_row = found_row[0]
        else:
            gap = False
            for row in tile_row:
                if row not in found_row:
                    gap = True
                else:
                    if gap:
                        low_row = row
                        break
        for tile in tiles:
            coffset = ord(tile[0]) - ord(low_col)
            if coffset < 0:
                coffset = coffset + len(tile_column)
            roffset = ord(tile[1]) - ord(low_row)
            if roffset < 0:
                roffset = roffset + len(tile_row)
            mgrs_idx[(first, second)][tile] = (coffset, roffset)
with open('mgrs_idx.pkl', 'wb') as file:
    pickle.dump(mgrs_idx, file)
