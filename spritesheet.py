import pygame


class Spritesheet:
    def __init__(self, filename):
        self.spritesheet = pygame.image.load(filename).convert()
        self.rect = self.spritesheet.get_rect()

    def get_image(self, colorkey=None, rect=(), size=(0, 0),
                  horizontally=False, vertically=False, angle=0):
        if len(rect) == 4:
            if type(rect[2]) in {int, float} and type(rect[3]) in {int, float}:
                image = pygame.Surface((rect[2], rect[3]))
            else:
                image = pygame.Surface(self.rect.size)
            image.blit(self.spritesheet, (0, 0), rect)
        else:
            image = pygame.Surface(self.rect.size)
            image.blit(self.spritesheet, (0, 0))
        image.set_colorkey(colorkey)
        if size != (0, 0):
            image = pygame.transform.scale(image, size)
        image = pygame.transform.flip(image, horizontally, vertically)
        image_copy = image.copy()
        image = pygame.transform.rotate(image_copy, angle)
        return image


if __name__ == '__main__':
    pass
