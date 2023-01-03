import cv2
import requests
import numpy as np
import threading

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


def download_image(lat1: float, lon1: float, lat2: float,
    lon2: float, zoom: int, url: str, headers: dict) -> np.ndarray:
    """
    Returns the satellite image of a rectangular area stored as a `numpy.ndarray` in BGR.

    Parameters
    ----------
    `(lat1, lon1)`: the coordinates (decimal degrees) of the top-left corner of the area.

    `(lat2, lon2)`: the coordinates (decimal degrees) of the bottom-right corner of the area.

    `zoom`: the zoom level.

    `url`: a tile url template.

    `headers`: a dictionary of HTTP headers.
    """
    scale = 1 << zoom

    # Find the pixel coordinates and tile coordinates of the area
    tl_proj_x, tl_proj_y = project_with_scale(lat1, lon1, scale)
    br_proj_x, br_proj_y = project_with_scale(lat2, lon2, scale)

    tl_pixel_x = int(tl_proj_x * TILE_SIZE)
    tl_pixel_y = int(tl_proj_y * TILE_SIZE)
    br_pixel_x = int(br_proj_x * TILE_SIZE)
    br_pixel_y = int(br_proj_y * TILE_SIZE)

    tl_tile_x = int(tl_proj_x)
    tl_tile_y = int(tl_proj_y)
    br_tile_x = int(br_proj_x)
    br_tile_y = int(br_proj_y)

    # Build the output image
    img_w = abs(tl_pixel_x - br_pixel_x)
    img_h = br_pixel_y - tl_pixel_y
    img = np.ndarray((img_h, img_w, 3), np.uint8)
    for i in range(tl_tile_y, br_tile_y + 1):
        for j in range(tl_tile_x, br_tile_x + 1):
            tile = download_tile(url.format(x=j, y=i, z=zoom), headers)

            # Find the pixel coordinates of the new tile relative to the output image
            tl_rel_x = j * TILE_SIZE - tl_pixel_x
            tl_rel_y = i * TILE_SIZE - tl_pixel_y
            br_rel_x = tl_rel_x + TILE_SIZE
            br_rel_y = tl_rel_y + TILE_SIZE

            # Define the part of the otuput image where the tile will be placed
            i_x_l = max(0, tl_rel_x)
            i_x_r = min(img_w + 1, br_rel_x)
            i_y_l = max(0, tl_rel_y)
            i_y_r = min(img_h + 1, br_rel_y)

            # Define how the tile will be cropped in case it is a border tile
            cr_x_l = max(0, -tl_rel_x)
            cr_x_r = TILE_SIZE + min(0, img_w - br_rel_x)
            cr_y_l = max(0, -tl_rel_y)
            cr_y_r = TILE_SIZE + min(0, img_h - br_rel_y)

            # Place the tile
            img[i_y_l:i_y_r, i_x_l:i_x_r] = tile[cr_y_l:cr_y_r, cr_x_l:cr_x_r]
    
    return img


def download_image_mt(lat1: float, lon1: float, lat2: float,
    lon2: float, zoom: int, url: str, headers: dict) -> np.ndarray:
    """
    A modified version of the download_image function that builds each row of tiles in
    a separate thread.
    
    Returns the satellite image of a rectangular area stored as a `numpy.ndarray` in BGR.

    Parameters
    ----------
    `(lat1, lon1)`: the coordinates (decimal degrees) of the top-left corner of the area.

    `(lat2, lon2)`: the coordinates (decimal degrees) of the bottom-right corner of the area.

    `zoom`: the zoom level.

    `url`: a tile url template.

    `headers`: a dictionary of HTTP headers.
    """
    
    scale = 1 << zoom

    # Find the pixel coordinates and tile coordinates of the area
    tl_proj_x, tl_proj_y = project_with_scale(lat1, lon1, scale)
    br_proj_x, br_proj_y = project_with_scale(lat2, lon2, scale)

    tl_pixel_x = int(tl_proj_x * TILE_SIZE)
    tl_pixel_y = int(tl_proj_y * TILE_SIZE)
    br_pixel_x = int(br_proj_x * TILE_SIZE)
    br_pixel_y = int(br_proj_y * TILE_SIZE)

    tl_tile_x = int(tl_proj_x)
    tl_tile_y = int(tl_proj_y)
    br_tile_x = int(br_proj_x)
    br_tile_y = int(br_proj_y)

    # Build the output image
    img_w = abs(tl_pixel_x - br_pixel_x)
    img_h = br_pixel_y - tl_pixel_y
    img = np.ndarray((img_h, img_w, 3), np.uint8)

    def build_row(row_number):
        for j in range(tl_tile_x, br_tile_x + 1):
            tile = download_tile(url.format(x=j, y=row_number, z=zoom), headers)

            # Find the pixel coordinates of the new tile relative to the output image
            tl_rel_x = j * TILE_SIZE - tl_pixel_x
            tl_rel_y = row_number * TILE_SIZE - tl_pixel_y
            br_rel_x = tl_rel_x + TILE_SIZE
            br_rel_y = tl_rel_y + TILE_SIZE

            # Define the part of the otuput image where the tile will be placed
            i_x_l = max(0, tl_rel_x)
            i_x_r = min(img_w + 1, br_rel_x)
            i_y_l = max(0, tl_rel_y)
            i_y_r = min(img_h + 1, br_rel_y)

            # Define how the tile will be cropped in case it is a border tile
            cr_x_l = max(0, -tl_rel_x)
            cr_x_r = TILE_SIZE + min(0, img_w - br_rel_x)
            cr_y_l = max(0, -tl_rel_y)
            cr_y_r = TILE_SIZE + min(0, img_h - br_rel_y)

            # Place the tile
            img[i_y_l:i_y_r, i_x_l:i_x_r] = tile[cr_y_l:cr_y_r, cr_x_l:cr_x_r]
    
    threads = []
    for i in range(tl_tile_y, br_tile_y + 1):
        thread = threading.Thread(target=build_row, args=[i])
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()
    
    return img


def image_size(lat1: float, lon1: float, lat2: float,
    lon2: float, zoom: int) -> tuple[int, int]:
    """ Returns the size of an image without downloading it. """

    scale = 1<<int(zoom)
    tl_proj_x, tl_proj_y = project_with_scale(lat1, lon1, scale)
    br_proj_x, br_proj_y = project_with_scale(lat2, lon2, scale)

    tl_pixel_x = int(tl_proj_x * TILE_SIZE)
    tl_pixel_y = int(tl_proj_y * TILE_SIZE)
    br_pixel_x = int(br_proj_x * TILE_SIZE)
    br_pixel_y = int(br_proj_y * TILE_SIZE)

    return abs(tl_pixel_x - br_pixel_x), br_pixel_y - tl_pixel_y
