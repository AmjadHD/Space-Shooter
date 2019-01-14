import pygame as pg


class SpriteSheet:
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert()
        self.rect = self.spritesheet.get_rect()

    def get_image(self, colorkey=None, rect=None, size=None,
                  horizontally=False, vertically=False, angle=0):
        if rect is not None:
            image = pg.Surface((rect[2], rect[3]))
            image.blit(self.spritesheet, (0, 0), rect)
        else:
            image = pg.Surface(self.rect.size)
            image.blit(self.spritesheet, (0, 0))
        image.set_colorkey(colorkey)
        if size is not None:
            image = pg.transform.scale(image, size)
        if horizontally or vertically:
            image = pg.transform.flip(image, horizontally, vertically)
        return pg.transform.rotate(image.copy(), angle)
