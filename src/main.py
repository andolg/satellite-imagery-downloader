import os
import json

from image_generation import generate_image

file_dir = os.path.dirname(__file__)

default_prefs = {
    'url': 'https://khms0.google.com/kh/v=932?x={x}&y={y}&z={z}',
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
    inputs = [0] * len(messages)

    print('Enter "r" to reset or "q" to exit.')
    i = 0
    while i < 5:
        inp = input(messages[i])
        if inp == 'q':
            return None
        if inp == 'r':
            return take_input(messages)

        try:
            inputs[i] = float(inp)
        except ValueError:
            print('Not a number.')
            continue

        i += 1

    return inputs


def run():
    with open(os.path.join(file_dir, 'preferences.json'), 'r') as f:
        prefs = json.loads(f.read())

    if not os.path.isdir(prefs['dir']):
        os.mkdir(prefs['dir'])

    if (prefs['region_ul'] == '') or (prefs['region_br'] == '') or (prefs['zoom'] == ''):
        messages = ['Upper-left lat: ', 'Upper-left lon: ', 'Bottom-right lat: ', 'Bottom-right lon: ', 'Zoom level: ']
        inputs = take_input(messages)
        if inputs is None:
            return
        else:
            lat1, lon1, lat2, lon2, zoom = inputs
            zoom = int(zoom)
    else:
        lat1, lon1 = prefs['region_ul'].split(',')
        lat1 = float(lat1)
        lon1 = float(lon1)

        lat2, lon2 = prefs['region_br'].split(',')
        lat2 = float(lat2)
        lon2 = float(lon2)

        zoom = int(prefs['zoom'])

    generate_image(lat1, lon1, lat2, lon2, zoom, prefs['url'], prefs['headers'], prefs['dir'])


prefs_path = os.path.join(file_dir, 'preferences.json')
if os.path.isfile(prefs_path):
    run()
else:
    with open(prefs_path, 'w') as f:
        f.write(json.dumps(default_prefs, indent=2))

    print(f'The preferences file has been created in {prefs_path}')
