import pygame as pg


RLEACCEL = pg.constants.RLEACCEL
class SpriteSheet:
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert()
        self.rect = self.spritesheet.get_rect()

    def get_image(self, rect=None, colorkey=(0, 0, 0)):
        if rect is not None:
            image = pg.Surface((rect[2], rect[3]))
            image.blit(self.spritesheet, (0, 0), rect)
        else:
            image = pg.Surface(self.rect.size)
            image.blit(self.spritesheet, (0, 0))
        image.set_colorkey(colorkey, RLEACCEL)
        return image

    def get_image_advanced(self, rect=None, size=None, colorkey=(0, 0, 0),
                  horizontally=False, vertically=False, angle=0):
        if rect is not None:
            image = pg.Surface((rect[2], rect[3]))
            image.blit(self.spritesheet, (0, 0), rect)
        else:
            image = pg.Surface(self.rect.size)
            image.blit(self.spritesheet, (0, 0))
        image.set_colorkey(colorkey, RLEACCEL)
        if size is not None:
            image = pg.transform.scale(image, size)
        if horizontally or vertically:
            image = pg.transform.flip(image, horizontally, vertically)
        return pg.transform.rotate(image.copy(), angle) if angle else image


def get_image(filename, colorkey=(0, 0, 0)):
    image = pg.image.load(filename).convert()
    image.set_colorkey(colorkey, RLEACCEL)
    return image

def write(screen, text, center, font, color):
    '''A function that draws a text on the screen'''
    text_rect = font.get_rect(text)
    text_rect.center = center
    font.render_to(screen, text_rect, None, color)
