import pygame_gui
import os
import pygame
import requests

KEYS = (pygame.K_PAGEDOWN, pygame.K_PAGEUP,
        pygame.K_UP, pygame.K_DOWN,
        pygame.K_LEFT, pygame.K_RIGHT,
        pygame.K_m, pygame.K_s, pygame.K_h, pygame.K_RETURN)
url_static = 'http://static-maps.yandex.ru/1.x/'
apikey = '40d1649f-0493-4b70-98ba-98533de7710b'

lon_delta = 300
lat_delta = 100


class Map:
    def __init__(self, coord, zoom, layer='map', size=(650, 450)):
        self.lon, self.lat = coord
        self.z = zoom
        self.layer = layer
        self.w, self.h = size
        self.find = False
        self.update_map()

    def update_map(self):
        self.params = {
            'l': self.layer,
            'll': f'{self.lon},{self.lat}',
            'z': self.z,
            'size': f'{self.w},{self.h}',
            'pt': f'{self.lon},{self.lat},flag'
        }
        if not self.find:
            self.params['pt'] = None
        response = requests.get(url_static, self.params)
        if not response:
            raise RuntimeError('Ошибка выполнения запроса')
        filename = 'temp_img.png'
        with open(filename, 'wb') as file:
            file.write(response.content)
        self.map = pygame.image.load(filename)
        os.remove(filename)

    def update(self, event):
        if event.key == pygame.K_PAGEUP:
            self.z = min(17, self.z + 1)
        elif event.key == pygame.K_PAGEDOWN:
            self.z = max(0, self.z - 1)
        elif event.key == pygame.K_RIGHT:
            self.lon = ((self.lon + 180 + lon_delta * 2 ** -self.z) % 360 - 180)
        elif event.key == pygame.K_LEFT:
            self.lon = ((self.lon + 180 - lon_delta * 2 ** -self.z) % 360 - 180)
        elif event.key == pygame.K_UP:
            self.lat = min(85, self.lat + lat_delta * 2 ** -self.z)
        elif event.key == pygame.K_DOWN:
            self.lat = max(-85, self.lat - lat_delta * 2 ** -self.z)
        elif event.key == pygame.K_RETURN:
            self.find = True
            if text_box.get_text():
                self.get_find(text_box.get_text())
                self.params['pt'] = f'{self.params["ll"]},flag'
        if not text_box.is_focused:
            if event.key == pygame.K_m:
                self.layer = 'map'
            elif event.key == pygame.K_s:
                self.layer = 'sat'
            elif event.key == pygame.K_h:
                self.layer = 'sat,skl'
        if event.key in KEYS:
            self.update_map()

    def get_find(self, add):
        geocoder_request = f"http://geocode-maps.yandex.ru/1.x/" \
                           f"?apikey={apikey}&geocode={add}&format=json"
        response = requests.get(geocoder_request)
        if not response:
            raise Exception('Ошибка выполнения запроса')
        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        toponym_address = toponym["Point"]["pos"]
        x, y = map(float, toponym_address.split())
        self.lon, self.lat = x, y
        self.update_map()



pygame.init()
screen = pygame.display.set_mode((650, 450))
coord = (38.2052612, 44.4192543)
z = 15
manager = pygame_gui.UIManager((650, 450))
text_box = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((10, 15), (200, 50)),
                                               manager=manager)
maps = Map(coord, z)
running = True
clock = pygame.time.Clock()
while running:
    time_delta = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            maps.update(event)
        manager.process_events(event)
    manager.update(time_delta)
    screen.blit(maps.map, (0, 0))
    manager.draw_ui(screen)
    pygame.display.flip()
pygame.quit()
