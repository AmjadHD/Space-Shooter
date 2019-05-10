from glob import glob
import os.path as osp

# constants:
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
FPS = 60
CAPTION = "Space Shooter"
# folders:
GAME_FOLDER = osp.dirname(__file__)
IMAGES_FOLDER = osp.join(GAME_FOLDER, 'images')
SPRITESHEETS_FOLDER = osp.join(IMAGES_FOLDER, 'spritesheets')
POWERUPS = glob(osp.join(IMAGES_FOLDER, 'powerups', '*png'))
SOUNDS_FOLDER = osp.join(GAME_FOLDER, 'sounds')
MUSIC = glob(osp.join(SOUNDS_FOLDER, '*mp3'))
