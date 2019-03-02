from glob import glob
from os.path import dirname, join

# constants:
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
FPS = 60
CAPTION = "Space Shooter"
# folders:
GAME_FOLDER = dirname(__file__)
IMAGES_FOLDER = join(GAME_FOLDER, 'images')
SPRITESHEETS_FOLDER = join(IMAGES_FOLDER, 'spritesheets')
POWERUPS = glob(join(IMAGES_FOLDER, 'powerups', '*png'))
SOUNDS_FOLDER = join(GAME_FOLDER, 'sounds')
MUSIC = glob(join(SOUNDS_FOLDER, '*mp3'))
