import os
from io import BytesIO
import pygame
import pygame_gui
import requests
from PIL import Image

KEYS = (pygame.KEYDOWN, pygame.K_PAGEUP, pygame.K_PAGEDOWN, pygame.K_UP, pygame.K_DOWN,
        pygame.K_LEFT, pygame.K_RIGHT, pygame.K_m, pygame.K_s, pygame.K_h, pygame.K_RETURN,
        pygame.K_z, pygame.K_x)
APIKEY_GEOCODER = "40d1649f-0493-4b70-98ba-98533de7710b"
url_static = 'https://static-maps.yandex.ru/1.x/'
w, h = size = 650, 450
delta = 180
z = 15


class Map:
    def __init__(self, coord, zoom, layer='map', size=size):
        self.lon, self.lat = coord
        self.flag_lon, self.flag_lat = 0, 0
        self.z = zoom
        self.layer = layer
        self.w, self.h = size
        self.map = None
        self.update_map()

    def update_map(self):
        params = {
            'l': self.layer,
            'll': f'{self.lon},{self.lat}',
            'z': self.z,
            'size': f'{self.w},{self.h}',
            'pt': f'{self.flag_lon},{self.flag_lat},flag'
        }
        response = requests.get(url_static, params)
        if not response:
            raise RuntimeError('Ошибка выполнения запроса')

        img = Image.open(BytesIO(response.content))
        img.save('image.png', 'png')
        self.map = pygame.image.load('image.png')
        os.remove('image.png')

    def update_params(self):
        address = search_box.text
        try:
            ll, spn = self.get_ll_spn(address)
            self.lon, self.lat = list(map(float, ll.split(',')))
            self.flag_lon, self.flag_lat = self.lon, self.lat

            toponym = self.get_geocode(address)
            search_box.set_text(toponym["name"])
        except TypeError:
            search_box.set_text('Неверный ввод')

    def update(self, event):
        lon_delta = delta / (2 ** self.z)
        lat_delta = delta / (2 ** self.z) / 2
        if event.key in (pygame.K_PAGEDOWN, pygame.K_z):
            self.z = max(0, self.z - 1)
        elif event.key in (pygame.K_PAGEUP, pygame.K_x):
            self.z = min(20, self.z + 1)
        elif event.key == pygame.K_LEFT:
            self.lon = (self.lon + 180 - lon_delta) % 360 - 180
        elif event.key == pygame.K_RIGHT:
            self.lon = (self.lon + 180 + lon_delta) % 360 - 180
        elif event.key == pygame.K_UP and abs(self.lat + lat_delta) < 85:
            self.lat += lat_delta
        elif event.key == pygame.K_DOWN and abs(self.lat - lat_delta) < 85:
            self.lat -= lat_delta
        elif pygame.key.get_pressed()[pygame.K_LCTRL]:
            if event.key == pygame.K_m:
                self.layer = 'map'
            elif event.key == pygame.K_s:
                self.layer = 'sat'
            elif event.key == pygame.K_h:
                self.layer = 'sat,skl'
        elif event.key == pygame.K_RETURN:
            self.update_params()
        if event.key in KEYS:
            mapapp.update_map()

    def reset_pt(self):
        self.flag_lat, self.flag_lon = 0, 0
        search_box.set_text('')
        mapapp.update_map()

    def get_geocode(self, address):
        geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

        geocoder_params = {
            "apikey": APIKEY_GEOCODER,
            "geocode": address,
            "format": "json"}

        response = requests.get(geocoder_api_server, params=geocoder_params)

        if not response:
            return

        json_response = response.json()
        features = json_response["response"]["GeoObjectCollection"][
            "featureMember"]
        toponym = features[0]["GeoObject"] if features else None
        return toponym

    def get_coords(self, address):
        toponym = self.get_geocode(address)
        toponym_coodrinates = toponym["Point"]["pos"]
        toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
        return tuple(map(float, (toponym_longitude, toponym_lattitude)))

    def get_ll_spn(self, address):
        toponym = self.get_geocode(address)
        if not toponym:
            return
        toponym_coodrinates = toponym["Point"]["pos"]
        ll = ','.join(toponym_coodrinates.split(" "))
        lc = toponym['boundedBy']["Envelope"]["lowerCorner"]
        uc = toponym['boundedBy']["Envelope"]["upperCorner"]
        lc_lo, lc_la = map(float, lc.split())
        uc_lo, uc_la = map(float, uc.split())
        spn = f'{(uc_lo - lc_lo)},{(uc_la - lc_la)}'
        return ll, spn


pygame.init()
screen = pygame.display.set_mode((650, 450))
coord = (38.2052612, 44.4192543)
mapapp = Map(coord, z)

clock = pygame.time.Clock()
FPS = 60

manager = pygame_gui.UIManager((650, 450))
search_box = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect(0, 0, 300, 100),
                                                 manager=manager)
reset_pt_btn = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(310, 0, 150, 30),
                                            text='Сбросить точку', manager=manager)

search_box.show()
running = True
while running:
    time_delta = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            mapapp.update(event)
            pygame.event.clear()
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == reset_pt_btn:
                    mapapp.reset_pt()
        manager.process_events(event)

    manager.update(time_delta)

    screen.blit(mapapp.map, (0, 0))
    manager.draw_ui(screen)
    pygame.display.flip()
