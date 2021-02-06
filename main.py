import pygame
import requests
from io import BytesIO

APIKEY_geocoder = "40d1649f-0493-4b70-98ba-98533de7710b"
url_static = "http://geocode-maps.yandex.ru/1.x/?"


class Map:
    def __init__(self, coord, zoom, layer='map', size=(650, 450)):
        self.lon, self.lat = coord
        self.z = zoom
        self.layer = layer
        self.size = size
        self.map = self.update_map()

    def update_map(self):
        params = {'l': self.layer,
                  'll': f'{self.lon},{self.lat}',
                  'z': self.z,
                  'size': '{},{}'.format(*self.size)}

        response = requests.get(url_static, params)
        if not response:
            raise RuntimeError('Ошибка выполнения запроса:\n' + response.url)

        self.map = pygame.image.load(BytesIO(response.content))


def get_geoobject(address):
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

    geocoder_params = {
        "apikey": APIKEY_geocoder,
        "geocode": address,
        "format": "json"}

    response = requests.get(geocoder_api_server, params=geocoder_params)

    if not response:
        return

    json_response = response.json()
    features = json_response["response"]["GeoObjectCollection"]["featureMember"]
    toponym = features[0]['GeoObject'] if features else None
    return toponym


def get_coord(address):
    toponym = get_geoobject(address)
    if not toponym:
        return
    toponym_coodrinates = toponym["Point"]["pos"]
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
    return tuple(map(float, (toponym_longitude, toponym_lattitude)))


def get_ll_spn(address):
    toponym = get_geoobject(address)
    if not toponym:
        return
    toponym_coodrinates = toponym["Point"]["pos"]
    ll = ','.join(toponym_coodrinates.split(" "))
    lc = toponym['boundedBy']['Envelope']['lowerCorner']
    uc = toponym['boundedBy']['Envelope']['upperCorner']
    lc_lo, lc_la = map(float, lc.split())
    uc_lo, uc_la = map(float, uc.split())
    spn = ','.join(map(str, (uc_lo - lc_lo, uc_la - lc_la)))
    return ll, spn


pygame.init()
w, h = size = 650, 450
screen = pygame.display.set_mode(size)

coord = '60.107412,55.047049'.split(',')
z = 17
mapapp = Map(coord, z)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.blit(mapapp.map, (0, 0))
    pygame.display.flip()
