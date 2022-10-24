import cv2
import requests
import numpy as np
import os.path
from tqdm import tqdm
from datetime import datetime

TILE_SIZE = 256


def download_tile(url, headers):
    response = requests.get(url, headers=headers)
    arr =  np.asarray(bytearray(response.content), dtype=np.uint8)
    return cv2.imdecode(arr, -1)


# Mercator projection 
# https://developers.google.com/maps/documentation/javascript/examples/map-coordinates
def project_with_scale(lat, lon, scale):
    siny = np.sin(lat * np.pi / 180)
    siny = min(max(siny, -0.9999), 0.9999)
    x = scale * (0.5 + lon / 360)
    y = scale * (0.5 - np.log((1 + siny) / (1 - siny)) / (4 * np.pi))
    return x, y


# (lat1, lon1) is the upper left corner of the region
# (lat2, lon2) is the bottom right corner of the region
# url should be a string with {x}, {y} and {z} in place of the tile coordinates and zoom
def generate_image(lat1: float, lon1: float, lat2: float, lon2: float, zoom: int, url: str, headers: str, save_dir: str):
    zoom = int(zoom)
    scale = 1 << zoom

    # Finding the pixel and tile coordinates of the region
    ul_proj_x, ul_proj_y = project_with_scale(lat1, lon1, scale)
    br_proj_x, br_proj_y = project_with_scale(lat2, lon2, scale)

    ul_pixel_x = int(ul_proj_x * TILE_SIZE)
    ul_pixel_y = int(ul_proj_y * TILE_SIZE)
    br_pixel_x = int(br_proj_x * TILE_SIZE)
    br_pixel_y = int(br_proj_y * TILE_SIZE)

    ul_tile_x = int(ul_proj_x)
    ul_tile_y = int(ul_proj_y)
    br_tile_x = int(br_proj_x)
    br_tile_y = int(br_proj_y)

    # Creating the output image
    img_w = abs(ul_pixel_x - br_pixel_x)
    img_h = br_pixel_y - ul_pixel_y
    img = np.ndarray((img_h, img_w, 3), np.uint8)
    for i in tqdm(range(ul_tile_y, br_tile_y + 1)):
        for j in range(ul_tile_x, br_tile_x + 1):
            tile = download_tile(url.format(x=j, y=i, z=zoom), headers)

            # Finding the coordinates of the new tile relative to the output image
            ul_rel_x = j * TILE_SIZE - ul_pixel_x
            ul_rel_y = i * TILE_SIZE - ul_pixel_y
            br_rel_x = ul_rel_x + TILE_SIZE
            br_rel_y = ul_rel_y + TILE_SIZE

            # Defining the part of the otuput image where the tile will be placed
            i_x_l = max(0, ul_rel_x)
            i_x_r = min(img_w + 1, br_rel_x)
            i_y_l = max(0, ul_rel_y)
            i_y_r = min(img_h + 1, br_rel_y)

            # Defining how the tile will be cropped in case it is a border tile
            t_x_l = max(0, -ul_rel_x)
            t_x_r = TILE_SIZE + min(0, img_w - br_rel_x)
            t_y_l = max(0, -ul_rel_y)
            t_y_r = TILE_SIZE + min(0, img_h - br_rel_y)

            # Placing the tile
            img[i_y_l:i_y_r, i_x_l:i_x_r] = tile[t_y_l:t_y_r, t_x_l:t_x_r]

    # Saving the image
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    cv2.imwrite(os.path.join(save_dir, f'img_{timestamp}.png'), img)
