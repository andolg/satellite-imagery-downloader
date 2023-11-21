import os
import json
import re
import cv2
from datetime import datetime

from image_downloading import download_image

file_dir = os.path.dirname(__file__)
prefs_path = os.path.join(file_dir, 'preferences.json')
default_prefs = {
        'url': 'https://mt.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        'tile_size': 256,
        'channels': 3,
        'dir': os.path.join(file_dir, 'images'),
        'headers': {
            'cache-control': 'max-age=0',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36'
        },
        'tl': '',
        'br': '',
        'zoom': ''
    }


def take_input(messages):
    inputs = []
    print('Enter "r" to reset or "q" to exit.')
    for message in messages:
        inp = input(message)
        if inp == 'q' or inp == 'Q':
            return None
        if inp == 'r' or inp == 'R':
            return take_input(messages)
        inputs.append(inp)
    return inputs


def run():
    with open(os.path.join(file_dir, 'preferences.json'), 'r', encoding='utf-8') as f:
        prefs = json.loads(f.read())

    if not os.path.isdir(prefs['dir']):
        os.mkdir(prefs['dir'])

    if (prefs['tl'] == '') or (prefs['br'] == '') or (prefs['zoom'] == ''):
        messages = ['Top-left corner: ', 'Bottom-right corner: ', 'Zoom level: ']
        inputs = take_input(messages)
        if inputs is None:
            return
        else:
            prefs['tl'], prefs['br'], prefs['zoom'] = inputs

    lat1, lon1 = re.findall(r'[+-]?\d*\.\d+|d+', prefs['tl'])
    lat2, lon2 = re.findall(r'[+-]?\d*\.\d+|d+', prefs['br'])

    zoom = int(prefs['zoom'])
    channels = int(prefs['channels'])
    tile_size = int(prefs['tile_size'])
    lat1 = float(lat1)
    lon1 = float(lon1)
    lat2 = float(lat2)
    lon2 = float(lon2)

    img = download_image(lat1, lon1, lat2, lon2, zoom, prefs['url'],
        prefs['headers'], tile_size, channels)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    name = f'img_{timestamp}.png'
    cv2.imwrite(os.path.join(prefs['dir'], name), img)
    print(f'Saved as {name}')


if os.path.isfile(prefs_path):
    run()
else:
    with open(prefs_path, 'w', encoding='utf-8') as f:
        json.dump(default_prefs, f, indent=2, ensure_ascii=False)

    print(f'Preferences file created in {prefs_path}')
