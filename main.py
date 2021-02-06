from io import BytesIO
import pygame
import requests

KEYS = (pygame.KEYDOWN, pygame.K_PAGEUP, pygame.K_UP, pygame.K_DOWN,
        pygame.K_LEFT, pygame.K_RIGHT)
url_static = 'https://static-maps.yandex.ru/1.x/'
w, h = size = 650, 450
delta = 180


class Map:
    def __init__(self, coord, zoom, layer='map', size=size):
        self.lon, self.lat = coord
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
            'size': f'{self.w},{self.h}'
        }
        response = requests.get(url_static, params)
        if not response:
            raise RuntimeError('Ошибка выполнения запроса')
        self.map = pygame.image.load(BytesIO(response.content))

    def update(self, event):
        lon_delta = delta / (2 ** self.z)
        lat_delta = delta / (2 ** self.z) / 2
        if event.key == pygame.K_PAGEDOWN:
            self.z = max(0, self.z - 1)
        elif event.key == pygame.K_PAGEUP:
            self.z = min(20, self.z + 1)
        elif event.key == pygame.K_LEFT:
            self.lon = (self.lon + 180 - lon_delta) % 360 - 180
        elif event.key == pygame.K_RIGHT:
            self.lon = (self.lon + 180 + lon_delta) % 360 - 180
        elif event.key == pygame.K_UP and abs(self.lat + lat_delta) < 85:
            self.lat += lat_delta
        elif event.key == pygame.K_DOWN and abs(self.lat - lat_delta) < 85:
            self.lat -= lat_delta
        if event.key in KEYS:
            mapapp.update_map()


pygame.init()
screen = pygame.display.set_mode((650, 450))
coord = (38.2052612, 44.4192543)
z = 0
mapapp = Map(coord, z)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            mapapp.update(event)

    screen.blit(mapapp.map, (0, 0))
    pygame.display.flip()
