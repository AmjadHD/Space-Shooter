import pygame as pg


class SpriteSheet:
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert()
        self.rect = self.spritesheet.get_rect()

    def get_image(self, colorkey=None, rect=(), size=(0, 0),
                  horizontally=False, vertically=False, angle=0):
        if len(rect) == 4:
            if isinstance(rect[2], (int, float)) and isinstance(rect[3], (int, float)):
                image = pg.Surface((rect[2], rect[3]))
            else:
                image = pg.Surface(self.rect.size)
            image.blit(self.spritesheet, (0, 0), rect)
        else:
            image = pg.Surface(self.rect.size)
            image.blit(self.spritesheet, (0, 0))
        image.set_colorkey(colorkey)
        if size != (0, 0):
            image = pg.transform.scale(image, size)
        image = pg.transform.flip(image, horizontally, vertically)
        return pg.transform.rotate(image.copy(), angle)


if __name__ == '__main__':
    pass
