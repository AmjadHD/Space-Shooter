from glob import glob
from os.path import dirname, join
from spritesheet import Spritesheet as Ss
import pygame as pg

gtk = pg.time.get_ticks
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
aconcepto100 = pg.font.Font(pg.font.match_font("a_Concepto"), 100)
aconcepto26 = pg.font.Font(pg.font.match_font("a_Concepto"), 26)
aconcepto20 = pg.font.Font(pg.font.match_font("a_Concepto"), 20)
aconcepto16 = pg.font.Font(pg.font.match_font("a_Concepto"), 16)
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
shipsheet = Ss(join(IMAGES_FOLDER, 'shipsheet.png'))
pg.display.set_icon(shipsheet.get_image(BLACK, [0, 192, 32, 50]))
# images:
POWERUPS = glob(join(IMAGES_FOLDER, 'powerups', '*png'))
mini_ship = shipsheet.get_image(BLACK, [0, 192, 32, 50], (20, 20))
mini_bomb = Ss(
    join(IMAGES_FOLDER, 'powerups', 'spaceMissiles_006.png')).get_image(
        BLACK, size=(15, 25))
