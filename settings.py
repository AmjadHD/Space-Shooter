from glob import glob
from os.path import dirname, join
from spritesheet import SpriteSheet
import pygame as pg
from pygame.freetype import SysFont


pg.init()
# constants:
BLACK = (0, 0, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
WIDTH = 480
HEIGHT = 600
FPS = 40
CAPTION = "Space Shooter"
# fonts
aconcepto100 = SysFont("a_Concepto", 100)
aconcepto26 = SysFont("a_Concepto", 26)
aconcepto20 = SysFont("a_Concepto", 20)
aconcepto16 = SysFont("a_Concepto", 16)
# folders:
GAME_FOLDER = dirname(__file__)
IMAGES_FOLDER = join(GAME_FOLDER, 'images')
SOUNDS_FOLDER = join(GAME_FOLDER, 'sounds')
# data:
# hs_file = join(GAME_FOLDER, 'high_score.txt')
# SOUNDS:
SOUNDS = glob(join(SOUNDS_FOLDER, 'sound_tracks', '**'))
MUSIC = glob(join(SOUNDS_FOLDER, '*mp3'))
# display:
# clock = pg.time.Clock()
SCREEN = pg.display.set_mode((WIDTH, HEIGHT), pg.RESIZABLE)
pg.display.set_caption(CAPTION)
shipsheet = SpriteSheet(join(IMAGES_FOLDER, 'shipsheet.png'))
pg.display.set_icon(shipsheet.get_image(BLACK, [0, 192, 32, 50]))
# images:
POWERUPS = glob(join(IMAGES_FOLDER, 'powerups', '*png'))
mini_ship = shipsheet.get_image(BLACK, [0, 192, 32, 50], (20, 20))
mini_bomb = SpriteSheet(
    join(IMAGES_FOLDER, 'powerups', 'spaceMissiles_006.png')).get_image(
        BLACK, size=(15, 25))
