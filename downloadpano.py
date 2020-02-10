# -*- coding: utf-8 -*-
# This file is based on code by Petr Gronat, Michal Havlena, and Jan Knopp,
#  and edited by Carl Doersch (cdoersch at cs dot cmu dot edu)
#
# download the panorama specified by panoid and return the data.
#
# More information on the general technique can be found in:
# GRONAT, P., HAVLENA , M., SIVIC , J., AND PAJDLA , T. 2011.
# Building streetview datasets for place recognition and city reconstruction. 
# Tech. Rep. CTU–CMP–2011–16, Czech Tech Univ.
#

'''
To run:
cd [directory where downloadpano.py is]

'''
import random
import numpy as np
import urllib, os, json, time
from PIL import Image
import urllib.request
from pathlib import Path
import pandas as pd
import datetime
from multiprocessing import Pool, Value

now=datetime.datetime.now()
yyyy_mm_dd= now.isoformat()[:10]

csv_file = 'ste-hya-centro-GSVpano.csv'
output_folder = f'ste-hya-centro_{yyyy_mm_dd}'
startnum = 5000
input_dir = Path('.')
output_dir = input_dir / output_folder
output_dir.mkdir(exist_ok=True)

def imtile(zoom, i, j, panoid, server):
  # fetch image
  fn = f'cbk?output=tile&zoom={zoom}&x={i}&y={j}&cb_client=maps_sv&fover=2&onerr=3&renderer=spherical&v=4&panoid={panoid}'
  cmd = f'https://cbks{server}.google.com/{fn}'
  return cmd

def downloadpano(iterrow, zoom = 4):
  index, row = iterrow
  #panoid = df_series['pano_Id']
  panoid = row.pano_Id
  #random between 1 and 3, inclusivement
  server = random.randint(0,3)

  if zoom == 4:
    tilex, tiley, tilew, tileh, imw = (13, 7, 512, 512, 13*512)
  elif zoom == 5:
    tilex, tiley, tilew, tileh, imw = (26, 14, 512, 512, 26 * 512)
    #notfound = false;

  #create numpy array zeros, with 3 channels, with right dimensions
  #im = tiley*tileh*tilex*tilew
  pano = []
  tile_count = 0
  for i in range(tilex):
    pano_col_tiles = []
    for j in range(tiley):
      tile_count += 1
      MyUrl = imtile(zoom, i, j, panoid, server)
      try:
        tile = Image.open(urllib.request.urlopen(MyUrl))
      except urllib.error.HTTPError as err:
        if err.code == 400:
          print(f'HTTPError {err.code}: Bad Request with {MyUrl}')
          break
        else:
          raise
      tile_np = np.array(tile)
      if j == tiley-1 and zoom == 4:
        tile_np = tile_np[:256, :, :]
        pano_col_tiles.append(tile_np)
        pano_col = np.concatenate(pano_col_tiles, axis = 0)
        pano.append(pano_col)
      else:
        pano_col_tiles.append(tile_np)
      time.sleep(0.1)

  if len(pano) != 0:
    pano = np.concatenate(pano, axis=1)
    pano = Image.fromarray(pano)
    #return pano
    num = index
    out_file = f"{num+5000:03d}.jpg"
    pano.save(output_dir.joinpath(out_file))
    print(f'Panorama no {num} successfully downloaded and saved on disk.')
  else:
    'No pano downloaded'
    return None

def metadata_to_dataframe(csv_file):
  df = pd.read_csv(csv_file, sep=';', parse_dates=['imageDate'], #index_col=['index'],
                   encoding='latin-1')
  df['pano_Id'] = df['pano_Id'].astype('str')
  mask = df['pano_Id'].str.len() < 64 #get panoId shorter than 64 characters to remove crowdsourced photos.
  df = df.loc[mask]  # takes 4 panoIds away --> 2835 to 2831
  #panoid_list = list(df.pano_Id)
  #return panoid_list
  return df
if __name__ == '__main__':

  start_index = 576
  df = metadata_to_dataframe(csv_file)

#  for index, row in df.iterrows():
#    print(index)
#    print(row)
  #  break
  pool = Pool(10)
  pool.map(downloadpano, df.iterrows())
  pool.terminate()
  pool.join()

#  for i in panoid_list:
#    count += 1
#    if count >= 576:
#      pano = downloadpano(i)

#      num = count + startnum
#      out_file = f'{int(num):03d}.jpg'
#      pano.save(output_dir.joinpath(out_file))
#      if count % 10 == 0:
#        print(f'Scrapping progress: {count} of {len(panoid_list)}')


