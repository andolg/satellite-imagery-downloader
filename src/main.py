import os
import json
import re
import cv2
from datetime import datetime

from image_downloading import download_image_mt

file_dir = os.path.dirname(__file__)
default_prefs = {
    'url': 'https://khms0.google.com/kh/v=937?x={x}&y={y}&z={z}',
    'dir': os.path.join(file_dir, 'images'),
    'region_ul': '',
    'region_br': '',
    'zoom': '',
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
    }
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
    with open(os.path.join(file_dir, 'preferences.json'), 'r') as f:
        prefs = json.loads(f.read())

    if not os.path.isdir(prefs['dir']):
        os.mkdir(prefs['dir'])

    if (prefs['region_ul'] == '') or (prefs['region_br'] == '') or (prefs['zoom'] == ''):
        messages = ['Upper-left corner: ', 'Bottom-right corner: ', 'Zoom level: ']
        inputs = take_input(messages)
        if inputs is None:
            return
        else:
            ul, br, zoom = inputs
            lat1, lon1 = re.findall(r'[+-]?\d*\.\d+|d+', ul)
            lat2, lon2 = re.findall(r'[+-]?\d*\.\d+|d+', br)
            zoom = int(zoom)
    else:
        lat1, lon1 = re.findall(r'[+-]?\d*\.\d+|d+', prefs['region_ul'])
        lat2, lon2 = re.findall(r'[+-]?\d*\.\d+|d+', prefs['region_br'])
        zoom = int(prefs['zoom'])

    lat1 = float(lat1)
    lon1 = float(lon1)
    lat2 = float(lat2)
    lon2 = float(lon2)

    img = download_image_mt(lat1, lon1, lat2, lon2, zoom, prefs['url'], prefs['headers'])

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    name = f'img_{timestamp}.png'
    cv2.imwrite(os.path.join(prefs['dir'], name), img)
    print(f'Saved as {name}')


prefs_path = os.path.join(file_dir, 'preferences.json')
if os.path.isfile(prefs_path):
    run()
else:
    with open(prefs_path, 'w') as f:
        f.write(json.dumps(default_prefs, indent=2))

    print(f'Preferences file created in {prefs_path}')
