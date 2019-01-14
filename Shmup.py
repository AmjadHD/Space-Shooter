# Space Shooter game by Amjad Ben Hedhili
from math import cos
from random import choice, random, randrange
from glob import glob
from os.path import join

import pygame as pg
from pygame.time import get_ticks
from pygame.freetype import SysFont
from pygame.math import Vector2 as vec

from spritesheet import SpriteSheet
from settings import *


pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
clock = pg.time.Clock()
pg.display.set_caption(CAPTION)
shipsheet = SpriteSheet(join(IMAGES_FOLDER, "spritesheets", 'shipsheet.png'))
pg.display.set_icon(shipsheet.get_image(BLACK, (0, 192, 32, 50)))
pg.event.set_allowed((pg.KEYDOWN, pg.KEYUP, pg.QUIT))

# images:
mini_ship = shipsheet.get_image(BLACK, (0, 192, 32, 50), (20, 20))
mini_bomb = SpriteSheet(join(IMAGES_FOLDER, 'powerups', 'spaceMissiles_006.png')
                        ).get_image(BLACK, size=(15, 25))
SOUNDS = tuple(pg.mixer.Sound(f) for f in glob(join(SOUNDS_FOLDER, 'sound_tracks', '**')))
# fonts
aconcepto100 = SysFont("a_Concepto", 100)
aconcepto26 = SysFont("a_Concepto", 26)
aconcepto20 = SysFont("a_Concepto", 20)
aconcepto14 = SysFont("a_Concepto", 14)


# the game
class Game:
    screen = screen

    def __init__(self):
        with open("highscore.txt", "r") as hs:
            try:
                self.highscore = int(hs.read())
            except:
                self.highscore = 0
        now = get_ticks()
        # game
        self.running = True
        self.game_over = False
        self.paused = False

        self.wait_time = now
        self.wait = True
        self.blink_time = now
        self.blink = False
        self.current_track = 0
        self.new_highscore = False
        self.restart = True
        self.player = Player()

        # grey mob
        self.grey_mob_time = now
        self.next_grey_mob = now
        self.get_grey_mob = True
        self.grey_mob_count = 0
        # red mob
        self.red_mob_time = now
        self.next_red_mob = now
        self.get_red_mob = False
        self.red_mob_count = 0
        # eye-like mob
        self.eyelike_mob_time = now
        self.next_eyelike_mob = now
        self.eyelike_mob_count = 0
        self.next_round_mob = now

        # groups
        self.all_sprites = pg.sprite.Group(self.player)
        self.mobs = pg.sprite.Group()
        self.stars = pg.sprite.Group()
        self.powerups = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.mob_bullets = pg.sprite.Group()
        self.rand_pos = randrange(40, HEIGHT // 3)

    def run(self):
        self.dt = clock.tick(FPS) // 2
        self.now = get_ticks()
        self.rand = random()

        # play music
        self.play_music()

        # handle events
        self.handle_events()

        # collisions:
        self.calculate_collisions()

        # mobs stuff
        self.get_mobs()

        # draw everything on the screen
        self.draw()

        # update
        self.all_sprites.update()
        pg.display.flip()

    def start(self):
        game_start = True
        while game_start:
            clock.tick(15)
            self.now = get_ticks()
            self.play_music()
            for event in pg.event.get():
                if event.type == pg.KEYUP:
                    game_start = False
                elif event.type == pg.QUIT:
                    pg.quit()
                    quit()

            self.screen.fill(BLACK)
            self.write("Space Shooter", (WIDTH / 2, HEIGHT / 4), aconcepto26, WHITE)
            self.write('Use Arrows To Move Space Bar To Shoot And B To Bomb',
                 (WIDTH / 2, HEIGHT / 2), aconcepto14, WHITE)
            if self.now - self.blink_time > 1000:
                self.blink_time = self.now
                self.blink = not self.blink
            self.write(f'High Score: {self.highscore}', (WIDTH // 2, HEIGHT * 2 // 3),
                 aconcepto26, WHITE)
            if self.blink:
                self.write('press any key', (WIDTH // 2, HEIGHT * 3 // 4),
                     aconcepto26, WHITE)

            # stars.update()
            pg.display.flip()

    def over(self):
        # game over
        while self.game_over:
            clock.tick(15)
            self.now = get_ticks()
            self.play_music()
            for event in pg.event.get():
                if event.type == pg.KEYUP and not self.wait:
                    self.game_over = False
                elif event.type == pg.QUIT:
                    pg.quit()
                    quit()

            if self.now - self.wait_time > 1500:
                self.wait = False
            # initialisation:
            if self.restart:
                ct = self.current_track
                score = self.player.score
                self.__init__()
                if score > self.highscore:
                    self.new_highscore = True
                    self.highscore = score
                    with open("highscore.txt", "w") as hs:
                        hs.write(str(self.highscore))

                self.game_over = True
                self.restart = False
                self.current_track = ct
            # draw
            self.screen.fill(BLACK)
            self.write("Space Shooter", (WIDTH // 2, HEIGHT // 4), aconcepto26, WHITE)
            self.write('Use Arrows To Move Space Bar To Shoot And B To Bomb',
                 (WIDTH / 2, HEIGHT / 2), aconcepto14, WHITE)
            if self.now - self.blink_time > 1000:
                self.blink_time = self.now
                self.blink = not self.blink
            if self.blink:
                if self.highscore:
                    self.write(f'New High Score: {self.highscore}',
                          (WIDTH // 2, HEIGHT // 3), aconcepto26, WHITE)
                else:
                    self.write('Game Over', (WIDTH // 2, HEIGHT // 3),
                           aconcepto26, WHITE)
                self.write('press any key', (WIDTH // 2, HEIGHT * 3 // 4),
                     aconcepto26, WHITE)

            # update
            pg.display.flip()

    def pause(self):
        while self.paused:
            clock.tick(15)
            self.play_music()
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_n:
                        self.paused = False
                elif event.type == pg.QUIT:
                    pg.quit()
                    quit()
            self.write('paused', (WIDTH // 2, HEIGHT // 2), aconcepto100, WHITE)
            pg.display.flip()

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_n:
                    self.paused = True
                elif event.key == pg.K_w:
                    self.player.weapon += 1
                    if self.player.weapon > self.player.power_level:
                        self.player.weapon = 1
                elif event.key == pg.K_h:
                    self.player.hold_fire = not self.player.hold_fire
                elif event.key == pg.K_b and self.player.bombs > 0:
                    self.player.bombs -= 1
                    self.player.bomb()
            elif event.type == pg.QUIT:
                self.running = False

    def draw(self):
        self.screen.fill(BLACK)
        for i in range(self.player.lives):
            self.screen.blit(mini_ship, ((WIDTH - 90) + 30 * i, 10))
        for i in range(self.player.bombs):
            self.screen.blit(mini_bomb, (110 + 30 * i, 5))
        # stars.draw(self.screen)
        self.all_sprites.draw(self.screen)
        self.write(f'Score:{self.player.score}', (WIDTH // 2, 10), aconcepto20, WHITE)
        self.write(f'weapon:{self.player.weapon}/{self.player.power_level}',
             (WIDTH * 3 // 4, 10), aconcepto14, RED)
        self.player.shield_bar()

    def write(self, text, center, font, color):
        '''A function that draws a text on the screen'''
        text_rect = font.get_rect(text)
        text_rect.center = center
        font.render_to(self.screen, text_rect, None, color)

    def get_mobs(self):
        if self.now - self.grey_mob_time > 10000:
            self.grey_mob_time = self.now
            self.get_grey_mob = True
        if self.now - self.next_grey_mob > 500 and self.get_grey_mob:
            self.next_grey_mob = self.now
            self.grey_mob_count += 1
            GreyMob(200, -50).add(self.all_sprites, self.mobs)
            if self.grey_mob_count > 5:
                self.grey_mob_count = 0
                self.get_grey_mob = False
        if self.now - self.red_mob_time > 8000:
            self.red_mob_time = self.now
            self.get_red_mob = True
        if self.now - self.next_red_mob > 200 and self.get_red_mob:
            self.red_mob_count += 1
            self.next_red_mob = self.now
            RedMob(500, -200).add(self.all_sprites, self.mobs)
            if self.red_mob_count > 5:
                self.red_mob_count = 0
                self.get_red_mob = False
        if self.now - self.next_round_mob > 6000:
            self.next_round_mob = self.now
            if self.rand > 0.6:
                RoundMob().add(self.all_sprites, self.mobs)
        if self.now - self.next_eyelike_mob > 12000:
            self.next_eyelike_mob = self.now
            if self.rand < 0.9:
                self.eyelike_mob_count = 0
                self.rand_pos = randrange(40, HEIGHT // 3)
        if self.now - self.eyelike_mob_time > 500 and self.eyelike_mob_count < 12:
            self.eyelike_mob_time = self.now
            self.eyelike_mob_count += 1
            EyeLikeMob(self.rand_pos).add(self.all_sprites, self.mobs)
        if len(self.mobs) < 5:
            for i in range(7):
                Asterroid().add(self.all_sprites, self.mobs)

    def calculate_collisions(self):
        for mob in pg.sprite.groupcollide(self.mobs, self.bullets, False, True):
            self.player.hit(mob)
        for mob in pg.sprite.spritecollide(self.player, self.mobs, True):
            self.player.get_hit(mob)
        for powerup in pg.sprite.spritecollide(self.player, self.powerups, True):
            self.player.get_powerup(powerup)
        for mob_bullet in pg.sprite.spritecollide(self.player, self.mob_bullets, True):
            self.player.get_hit(mob_bullet)
        self.player.set_power()

    def play_music(self):
        if not pg.mixer.music.get_busy():
            pg.mixer.music.load(MUSIC[self.current_track])
            pg.mixer.music.play(1)
            self.current_track += 1
            if self.current_track == len(MUSIC):
                self.current_track = 0
        if self.paused:
            pg.mixer.music.pause()
        else:
            pg.mixer.music.unpause()


# the sprites:
class Player(pg.sprite.Sprite):
    '''The spaceship sprite'''
    ship_imgs = {
        'x': (0, 32, 67, 99),
        'y': 192,
        'width': (32, 32, 30, 30),
        'height': 50
    }

    def __init__(self):
        super(Player, self).__init__()
        self.image = shipsheet.get_image(BLACK, (0, 192, 32, 50), (40, 63))
        self.rect = self.image.get_rect()
        self.radius = 10
        self.rect.bottom = HEIGHT - 10
        self.rect.centerx = WIDTH / 2
        self.frame = 0
        self.lives = 3
        self.shield = 100
        self.score = 0
        self.power_level = 1
        self.weapon = 1
        self.bombs = 1
        self.hidden = False
        self.flip = False
        self.hold_fire = True
        self.shoot_time = get_ticks()
        self.missile_time = self.shoot_time
        self.power_time = self.shoot_time
        self.strive = self.shoot_time
        self.hide_time = self.shoot_time

    def update(self):
        if self.hidden and get_ticks() - self.hide_time > 1500:
            self.hidden = False
            self.bomb()
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10
        key_state = pg.key.get_pressed()
        if (key_state[pg.K_LEFT]
                or key_state[pg.K_RIGHT]) and (key_state[pg.K_UP]
                                               or key_state[pg.K_DOWN]):
            step = game.dt / 1.414
        else:
            step = game.dt
        if key_state[pg.K_RIGHT] or key_state[pg.K_LEFT]:
            if key_state[pg.K_LEFT]:
                self.rect.x -= step
                self.flip = False
            elif key_state[pg.K_RIGHT]:
                self.rect.x += step
                self.flip = True
            now = get_ticks()
            if now - self.strive > 100:
                self.strive = now
                self.frame += 1
                if self.frame > 3:
                    self.frame = 3
        else:
            self.frame = 0
        if key_state[pg.K_UP]:
            self.rect.y -= step
        elif key_state[pg.K_DOWN]:
            self.rect.y += step
        if key_state[pg.K_SPACE] or self.hold_fire:
            self.shoot()
        if self.rect.right >= WIDTH:
            self.rect.right = WIDTH 
        elif self.rect.left <= 0:
            self.rect.left = 0
        if HEIGHT <= self.rect.bottom < HEIGHT + 100:
            self.rect.bottom = HEIGHT
        elif self.rect.top <= 0:
            self.rect.top = 0
        self.image = shipsheet.get_image(BLACK, (
            self.ship_imgs['x'][self.frame], self.ship_imgs['y'],
            self.ship_imgs['width'][self.frame], self.ship_imgs['height']
        ), (40, 63), self.flip)

    def hide(self):
        self.hidden = True
        self.hide_time = get_ticks()
        self.rect.center = (2 * WIDTH, 2 * HEIGHT)

    def launch_missile(self):
        Missile((self.rect.left, self.rect.centery)).add(game.all_sprites, game.bullets)
        Missile((self.rect.right, self.rect.centery)).add(game.all_sprites, game.bullets)
        Missile((self.rect.centerx, self.rect.top)).add(game.all_sprites, game.bullets)

    def shoot(self):
        now = get_ticks()
        if not self.hidden:
            if now - self.shoot_time > 250:
                self.shoot_time = now
                if self.weapon == 1:
                    SOUNDS[2].play()
                    Bullet(self.rect.centerx, self.rect.top).add(
                        game.all_sprites, game.bullets)
                elif self.weapon == 2:
                    SOUNDS[3].play()
                    Bullet(self.rect.left, self.rect.centery).add(
                        game.all_sprites, game.bullets)
                    Bullet(self.rect.right, self.rect.centery).add(
                        game.all_sprites, game.bullets)
                elif self.weapon == 3:
                    SOUNDS[2].play()
                    SOUNDS[3].play()
                    Bullet(self.rect.left, self.rect.centery, -1, 30).add(
                        game.all_sprites, game.bullets)
                    Bullet(self.rect.right, self.rect.centery, 1, -30).add(
                        game.all_sprites, game.bullets)
                    Bullet(self.rect.centerx, self.rect.top).add(
                        game.all_sprites, game.bullets)
                elif self.weapon == 5:
                    SOUNDS[2].play()
                    SOUNDS[3].play()
                    Bullet(self.rect.left, self.rect.centery).add(
                        game.all_sprites, game.bullets)
                    Bullet(self.rect.right, self.rect.centery).add(
                        game.all_sprites, game.bullets)
                    Bullet(self.rect.centerx, self.rect.top).add(
                        game.all_sprites, game.bullets)
                elif self.weapon == 6:
                    SOUNDS[2].play()
                    SOUNDS[3].play()
                    Bullet(self.rect.left, self.rect.centery).add(
                        game.all_sprites, game.bullets)
                    Bullet(self.rect.right, self.rect.centery).add(
                        game.all_sprites, game.bullets)
                    Bullet(self.rect.centerx, self.rect.top).add(
                        game.all_sprites, game.bullets)
                    Bullet(self.rect.left, self.rect.centery, -1.2, 35).add(
                        game.all_sprites, game.bullets)
                    Bullet(self.rect.right, self.rect.centery, 1.2, -35).add(
                        game.all_sprites, game.bullets)
                elif self.weapon == 7:
                    SOUNDS[2].play()
                    SOUNDS[3].play()
                    self.launch_missile()
                    Bullet(self.rect.left, self.rect.centery, -0.6, 16).add(
                        game.all_sprites, game.bullets)
                    Bullet(self.rect.right, self.rect.centery, 0.6, -16).add(
                        game.all_sprites, game.bullets)
                    Bullet(self.rect.centerx, self.rect.top).add(
                        game.all_sprites, game.bullets)
                    Bullet(self.rect.left, self.rect.centery, -1.2, 35).add(
                        game.all_sprites, game.bullets)
                    Bullet(self.rect.right, self.rect.centery, 1.2, -35).add(
                        game.all_sprites, game.bullets)
            if now - self.missile_time > 300 and self.weapon == 6:
                self.missile_time = now
                self.launch_missile()
            elif now - self.missile_time > 400 and self.weapon == 5:
                self.missile_time = now
                self.launch_missile()
            elif now - self.missile_time > 500 and self.weapon == 4:
                self.missile_time = now
                SOUNDS[2].play()
                SOUNDS[3].play()
                self.launch_missile()

    def hit(self, mob):
        if type(mob) is not Asterroid:
            self.score += int(100 - mob.radius)
        mob.shield -= 16
        if mob.shield < 0:
            mob.kill()
            mx = max(mob.rect.width, mob.rect.height)
            game.all_sprites.add(Explosion(mob.rect.center, (mx, mx)))
            if 0.1 < game.rand < 0.4:
                Asterroid().add(game.all_sprites, game.mobs)
            elif game.rand > 0.8 and type(mob) is RoundMob:
                    Powerup(mob.rect.center).add(game.all_sprites, game.powerups)
            elif game.rand > 0.9 and isinstance(mob, (GreyMob, RedMob, EyeLikeMob)):
                    Powerup(mob.rect.center).add(game.all_sprites, game.powerups)
            elif game.rand > 0.99:
                Powerup(mob.rect.center).add(game.all_sprites, game.powerups)
        else:
            mx = max(mob.rect.width // 2, mob.rect.height // 2)
            game.all_sprites.add(Explosion(mob.rect.center, (mx, mx)))

    def get_hit(self, object):
        SOUNDS[4].play()
        self.shield -= object.radius * 2
        if self.weapon == self.power_level:
            self.weapon -= 1
            if self.weapon < 1:
                self.weapon = 1
        self.power_level -= 1
        if self.power_level < 1:
            self.power_level = 1
        if not self.hidden:
            mx = max(object.rect.width // 2, object.rect.height // 2)
            game.all_sprites.add(Explosion(object.rect.center, (mx, mx)))
        if self.shield <= 0:
            self.shield = 100
            if self.bombs < 1:
                self.bombs = 1
            game.all_sprites.add(Explosion(self.rect.center, (150, 150)))
            self.lives -= 1
            if self.lives > 0:
                self.hide()
            else:
                self.lives = 0
                self.kill()
        if not self.lives:
            game.game_over = True
            game.restart = True
            game.wait_time = get_ticks()
            game.wait = True

    def get_powerup(self, powerup):
        if powerup.type == 0:
            SOUNDS[6].play()
            self.power_level += 1
            if self.power_level <= 7:
                self.weapon += 1
            self.power_time = get_ticks()
        elif powerup.type == 1:
            self.shield += randrange(10, 30)
            self.power_time = get_ticks()
            if self.shield >= 100:
                self.shield = 100
        elif powerup.type == 2:
            self.bombs += 1
            if self.bombs < 0:
                self.bombs = 0
            elif self.bombs > 3:
                self.bombs = 3

    def set_power(self):
        now = get_ticks()
        if now - self.power_time > 10000:
            self.power_time = now
            self.power_level -= 1
            if self.power_level < 1:
                self.power_level = 1
            elif self.power_level > 7:
                self.power_level = 7
            if self.weapon > self.power_level:
                self.weapon = self.power_level
            SOUNDS[4].play()

    def bomb(self):
        SOUNDS[8].play()
        for mob in game.mobs:
            mob.shield -= 50
            if mob.shield < 0:
                mob.kill()
                mx = max(mob.rect.width, mob.rect.height)
                game.all_sprites.add(Explosion(mob.rect.center, (mx, mx)))
                if type(mob) is not Asterroid:
                    self.score += 100 - mob.radius

    def shield_bar(self):
        color = RED if self.shield < 20 else (36, 218, 181)
        pg.draw.rect(game.screen, color, (0, 0, self.shield, 20))
        pg.draw.rect(game.screen, WHITE, (0, 0, 100, 20), 2)
        if self.shield > 0:
            game.write(f'{self.shield}%', (50, 10), aconcepto14, RED)


class Star(pg.sprite.Sprite):
    '''The stars in the background'''

    def __init__(self):
        super(Star, self).__init__()
        self.rand = randrange(4, 8)
        self.image = pg.Surface((self.rand, self.rand))
        self.rect = self.image.get_rect()
        pg.draw.circle(self.image, WHITE, self.rect.center, self.rand // 2)
        self.image.set_colorkey(BLACK)
        self.rect.center = (randrange(WIDTH), randrange(-150, HEIGHT))

    def update(self):
        if self.rand < 6:
            self.rect.y += 0.2 * game.dt
        else:
            self.rect.y += 0.25 * game.dt
        if self.rect.top > HEIGHT:
            self.rect.center = (randrange(WIDTH), randrange(-150, 0))


class Bullet(pg.sprite.Sprite):
    '''The player's lazer bullets'''
    spritesheet = SpriteSheet(join(IMAGES_FOLDER, 'guns', 'laser.png'))

    def __init__(self, x, y, direction=0, rot=0):
        super(Bullet, self).__init__()
        self.direction = direction
        self.rot = rot
        self.image = Bullet.spritesheet.get_image(BLACK, angle=self.rot)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y

    def update(self):
        self.rect.y -= 2 * game.dt
        self.rect.x += self.direction * game.dt
        if self.rect.bottom < 0:
            self.kill()


class Missile(pg.sprite.Sprite):
    '''The player's guided missiles'''
    image = SpriteSheet(join(IMAGES_FOLDER, 'guns', 'missile.png')
                        ).get_image(BLACK)

    def __init__(self, center):
        super(Missile, self).__init__()
        self.max_speed = 18
        self.center = center
        self.image_copy = self.image.copy()
        self.rect = self.image.get_rect()
        self.target = choice(game.mobs.sprites())
        self.pos = vec(self.center)
        self.vel = vec(0, -self.max_speed / 2)
        self.acc = vec(0, 0)
        self.rect.center = self.pos
        self.radius = 15
        self.shield = 5

    def seek(self, target):
        self.desired = (target - self.pos).normalize() * self.max_speed
        self.steer = self.desired - self.vel
        if self.steer.length() > 1:
            self.steer.scale_to_length(1)
        return self.steer

    def update(self):
        self.acc = self.seek(self.target.rect.center)
        if not self.target.alive() or type(self.target) is Asterroid:
            self.target = choice(game.mobs.sprites())
        self.vel += self.acc
        self.normal = vec(0, self.rect.centery)
        self.image = pg.transform.rotate(self.image_copy,
                                         self.vel.angle_to(self.normal) + 180)
        if self.vel.length() > self.max_speed:
            self.vel.scale_to_length(self.max_speed)
        self.pos += self.vel
        if self.pos.x < 0 or self.pos.x > WIDTH or self.pos.y > HEIGHT or self.pos.y < 0:
            self.kill()
        self.rect.center = self.pos


class MobBullet(pg.sprite.Sprite):
    '''The mob's bullets'''
    mobsheet = SpriteSheet(join(IMAGES_FOLDER, "spritesheets", 'mobsheet.png'))
    image = mobsheet.get_image(BLACK, (0, 640, 32, 32), (16, 16))
    mob_missile_imgs = {
        'x': (0, 32, 64, 128),
        'y': 640,
        'width': 32,
        'height': 32
    }

    def __init__(self, center):
        super(MobBullet, self).__init__()
        self.center = center
        self.frame = 0
        self.max_speed = 6
        self.rect = self.image.get_rect()
        self.pos = vec(self.center)
        self.vel = (
            game.player.rect.center - self.pos).normalize() * 1.5 * self.max_speed
        self.acc = vec(0, 0)
        self.rect.center = self.pos
        self.radius = 5
        self.shield = 5
        self.next = get_ticks()

    def seek(self, target):
        self.desired = (target - self.pos).normalize() * self.max_speed
        self.steer = (self.desired - self.vel)
        if self.steer.length() > 0.4:
            self.steer.scale_to_length(0.4)
        return self.steer

    def update(self):
        now = get_ticks()
        if now - self.next > 20:
            self.next = now
            self.frame += 1
            if self.frame == 4:
                self.frame = 0
        self.acc = vec(0, 0)
        self.vel += self.acc
        if self.vel.length() > self.max_speed:
            self.vel.scale_to_length(self.max_speed)
        self.pos += self.vel
        if not (0 <= self.pos.x <= WIDTH and 0 <= self.pos.y <= HEIGHT):
            self.kill()
        self.image = self.mobsheet.get_image(BLACK, (
            self.mob_missile_imgs['x'][self.frame],
            self.mob_missile_imgs['y'], self.mob_missile_imgs['width'],
            self.mob_missile_imgs['height']
        ), (16, 16))
        self.rect.center = self.pos


class MobMissile(pg.sprite.Sprite):
    '''The mob's guided missiles'''
    mobsheet = SpriteSheet(join(IMAGES_FOLDER, "spritesheets", 'mobsheet.png'))
    image = mobsheet.get_image(BLACK, (0, 0, 16, 40))
    mob_missile_imgs = {
        'x': (0, 16, 32, 48),
        'y': 0,
        'width': 16,
        'height': 40
    }

    def __init__(self, center):
        super(MobMissile, self).__init__()
        self.center = center
        self.frame = 0
        self.max_speed = 6
        self.rect = self.image.get_rect()
        self.pos = vec(self.center)
        self.vel = (
            game.player.rect.center - self.pos).normalize() * 1.5 * self.max_speed
        self.acc = vec(0, 0)
        self.rect.center = self.pos
        self.radius = 5
        self.shield = 5
        self.next = get_ticks()

    def seek(self, target):
        self.desired = (target - self.pos).normalize() * self.max_speed
        self.steer = (self.desired - self.vel)
        if self.steer.length() > 0.4:
            self.steer.scale_to_length(0.4)
        return self.steer

    def update(self):
        now = get_ticks()
        if now - self.next > 20:
            self.next = now
            self.frame += 1
            if self.frame == 4:
                self.frame = 0
        self.acc = self.seek(game.player.rect.center)
        self.vel += self.acc
        if self.vel.length() > self.max_speed:
            self.vel.scale_to_length(self.max_speed)
        self.pos += self.vel
        if not (0 <= self.pos.x <= WIDTH and 0 <= self.pos.y <= HEIGHT):
            self.kill()
        self.image = self.mobsheet.get_image(BLACK, (
            self.mob_missile_imgs['x'][self.frame],
            self.mob_missile_imgs['y'], self.mob_missile_imgs['width'],
            self.mob_missile_imgs['height']
        ))
        self.rect.center = self.pos


class Asterroid(pg.sprite.Sprite):
    '''The rocks floating in the space'''
    meteors = tuple(pg.image.load(img).convert() for img in glob(join(IMAGES_FOLDER, 'meteors', '*png')))

    def __init__(self):
        super(Asterroid, self).__init__()
        self.image = self.meteors[randrange(len(self.meteors))]
        self.image_copy = self.image.copy()
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self.rect.bottom = 0
        self.rect.x = randrange(WIDTH - self.rect.width)
        self.rect.y = randrange(-200, -100)
        self.rotation = 0
        self.speedx = randrange(-6, 6)
        self.speedy = randrange(4, 6)
        self.rot_speed = randrange(-8, 8)
        self.radius = int(self.rect.width * 0.85 / 2)
        self.shield = int(self.radius / 2)
        self.rot_time = get_ticks()

    def rotate(self):
        now = get_ticks()
        if now - self.rot_time > 50:
            self.rot_time = now
            self.rotation = (self.rotation + self.rot_speed) % 360
            new_image = pg.transform.rotate(self.image_copy, self.rotation)
            center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = center
            self.image.set_colorkey(WHITE)

    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:
            self.rect.x = randrange(WIDTH - self.rect.width)
            self.rect.y = randrange(-100, -40)
            self.speedx = randrange(-6, 6)
            self.speedy = randrange(4, 6)


class Explosion(pg.sprite.Sprite):
    '''A class for all types of explosions'''
    explosion_sheet = SpriteSheet(join(IMAGES_FOLDER, "spritesheets", 'explsheet.png'))
    explosion_imgs = {
        'x': tuple(j * 100 for i in range(8) for j in range(9)),
        'y': tuple(i * 100 for i in range(8) for j in range(9)),
        'width': 100,
        'height': 100
    }

    def __init__(self, center, size):
        super(Explosion, self).__init__()
        self.size = size
        self.frame = 0
        self.image = self.explosion_sheet.get_image(BLACK, (0, 0, 100, 100),
                                                    self.size)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.time = get_ticks()

    def update(self):
        now = get_ticks()
        if now - self.time > 1:
            self.time = now
            self.frame += 6
            if self.frame == len(self.explosion_imgs['x']):
                self.kill()
            else:
                center = self.rect.center
                self.image = self.explosion_sheet.get_image(BLACK, (
                    self.explosion_imgs['x'][self.frame],
                    self.explosion_imgs['y'][self.frame],
                    self.explosion_imgs['width'],
                    self.explosion_imgs['height']
                ), self.size)
                self.rect = self.image.get_rect()
                self.rect.center = center


class Powerup(pg.sprite.Sprite):
    '''All the POWERUPS: shield, weapon...'''
    POWERUPS = tuple(pg.image.load(f).convert()
                     for f in glob(join(IMAGES_FOLDER, 'powerups', '*png')))

    def __init__(self, center):
        super(Powerup, self).__init__()
        self.type = randrange(3)
        self.image = self.POWERUPS[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.center = center
        self.rect.center = center
        self.up = True

    def update(self):
        if self.rect.centery < self.center[1] - 50:
            self.up = False
        if self.up:
            self.rect.y -= game.dt / 2
        else:
            self.rect.y += game.dt / 4
        if self.rect.top > HEIGHT:
            self.kill()


class GreyMob(pg.sprite.Sprite):
    '''elongated grey alienship'''
    image = SpriteSheet(join(IMAGES_FOLDER, "mobs", 'greymob.png')
                                 ).get_image(BLACK, size=(100, 100))

    def __init__(self, x, y):
        super(GreyMob, self).__init__()
        self.max_speed = 10
        self.approach_radius = 100
        self.x = x
        self.y = y
        self.xd = x
        self.yd = y + 200
        self.steer_force = 2
        self.rect = self.image.get_rect()
        self.pos = vec(self.x, self.y)
        self.vel = vec(0, self.max_speed)
        self.acc = vec(0, 0)
        self.radius = 50
        self.shield = 17
        self.right = True
        self.next = get_ticks()
        self.shoot_time = self.next
        self.dtime = self.next
        self.rect.center = self.pos

    def shoot(self):
        now = get_ticks()
        if now - self.shoot_time > 3000:
            self.shoot_time = now
            MobBullet(self.rect.center).add(game.all_sprites, game.mob_bullets)

    def seek_with_approach(self, target):
        self.desired = (target - self.pos)
        dist = self.desired.length()
        self.desired.normalize_ip()
        if dist < self.approach_radius:
            self.desired *= dist / self.approach_radius * self.max_speed
        else:
            self.desired *= self.max_speed
        self.steer = (self.desired - self.vel)
        if self.steer.length() > self.steer_force:
            self.steer.scale_to_length(self.steer_force)
        return self.steer

    def update(self):
        self.shoot()
        now = get_ticks()
        if not ((self.xd, self.yd) - self.pos).length() == 0:
            self.acc = self.seek_with_approach((self.xd, self.yd))
        if now - self.dtime > 2000:
            self.dtime = now
            self.yd += 400
            if self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:
                self.kill()
            if self.right:
                self.xd += 100
                self.right = False
            else:
                self.xd -= 100
                self.right = True
        self.vel += self.acc
        if self.vel.length() > self.max_speed:
            self.vel.scale_to_length(self.max_speed)
        self.pos += self.vel
        self.rect.center = self.pos


class RedMob(pg.sprite.Sprite):
    '''The elongted red alienship'''

    def __init__(self, x, y):
        super(RedMob, self).__init__()
        self.max_speed = 10
        self.approach_radius = 100
        self.image = SpriteSheet(join(IMAGES_FOLDER, "mobs", 'redmob.png')
                                 ).get_image(BLACK, size=(58, 100))
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.xd = x
        self.yd = y + 200
        self.steer_force = 2
        self.pos = vec(self.x, self.y)
        self.vel = vec(0, self.max_speed)
        self.acc = vec(0, 0)
        self.radius = 40
        self.shield = 10
        self.right = True
        self.next = get_ticks()
        self.shoot_time = self.next
        self.dtime = self.next
        self.rect.center = self.pos
        self.c = 0
        self.then = self.next

    def shoot(self):
        now = get_ticks()
        if now - self.shoot_time > 3000:
            self.shoot_time = now
            MobBullet(self.rect.center).add(game.all_sprites, game.mob_bullets)

    def seek_with_approach(self, target):
        self.desired = (target - self.pos)
        dist = self.desired.length()
        self.desired.normalize_ip()
        if dist < self.approach_radius:
            self.desired *= dist / self.approach_radius * self.max_speed
        else:
            self.desired *= self.max_speed
        self.steer = (self.desired - self.vel)
        if self.steer.length() > self.steer_force:
            self.steer.scale_to_length(self.steer_force)
        return self.steer

    def update(self):
        self.shoot()
        now = get_ticks()
        if now - self.then > 300:
            self.then = now
            self.c = (self.c + 5) % 360
            # self.SpriteSheet = (self.SpriteSheet + 1) % 360
        self.acc = vec(cos(self.c) * self.max_speed - 10, 10)
        # if not ((self.xd, self.yd) - self.pos).length() == 0:
        # self.acc = self.seek_with_approach((self.xd, self.yd))
        if now - self.dtime > 2000:
            self.dtime = now
            self.yd += 400
            if self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:
                self.kill()
            if self.right:
                self.xd += 100
                self.right = False
            else:
                self.xd -= 100
                self.right = True
        self.vel += self.acc
        if self.vel.length() > self.max_speed:
            self.vel.scale_to_length(self.max_speed)
        self.pos += self.vel
        self.rect.center = self.pos


class EyeLikeMob(pg.sprite.Sprite):
    '''The eye-like alienship'''
    mobsheet = SpriteSheet(join(IMAGES_FOLDER, "spritesheets", 'eyelike_mobsheet.png'))
    image = mobsheet.get_image(WHITE, (0, 0, 31, 80))
    mob_imgs = {
        'x': (0, 31, 63, 95, 127, 175, 223, 270),
        'y': 0,
        'width': (31, 32, 32, 32, 48, 48, 48, 48),
        'height': 80
    }

    def __init__(self, y):
        super(EyeLikeMob, self).__init__()
        self.frame = 0
        self.y = y
        self.yd = self.y
        self.max_speed = 4
        self.steer_force = 0.2
        self.approach_radius = 100
        self.rect = self.image.get_rect()
        self.pos = vec(WIDTH + 40, self.y)
        self.vel = vec(-self.max_speed, 0)
        self.acc = vec(0, 0)
        self.xd = (-100, WIDTH + 100)[randrange(2)]
        self.radius = 50
        self.shield = 12
        self.next = get_ticks()
        self.shoot_time = self.next
        self.switch = False
        self.rect.center = self.pos

    def shoot(self):
        now = get_ticks()
        if now - self.shoot_time > 4000:
            self.shoot_time = now
            MobBullet(self.rect.center).add(game.all_sprites, game.mob_bullets)

    def seek_with_approach(self, target):
        self.desired = (target - self.pos)
        dist = self.desired.length()
        self.desired.normalize_ip()
        if dist < self.approach_radius:
            self.desired *= dist / self.approach_radius * self.max_speed
        else:
            self.desired *= self.max_speed
        self.steer = (self.desired - self.vel)
        if self.steer.length() > self.steer_force:
            self.steer.scale_to_length(self.steer_force)
        return self.steer

    def update(self):
        self.shoot()
        now = get_ticks()
        if now - self.next > 500:
            self.next = now
            self.frame += 1
            if self.frame == len(self.mob_imgs['x']):
                self.frame = 0
        self.image = self.mobsheet.get_image(
            WHITE, (self.mob_imgs['x'][self.frame], self.mob_imgs['y'],
                    self.mob_imgs['width'][self.frame],
                    self.mob_imgs['height']))
        if self.rect.right < 0:
            self.kill()
        self.vel += self.acc
        self.pos += self.vel
        self.rect.center = self.pos


class RoundMob(pg.sprite.Sprite):
    '''The round alienship'''
    mobsheet = SpriteSheet(join(IMAGES_FOLDER, "spritesheets", 'mobsheet.png'))
    mob_imgs = {
        'x': (0, 95, 190, 285, 385, 480, 575),
        'y': (45, 270, 496, 718),
        'width': (95, 95, 95, 100, 95, 95, 95),
        'height': 90
    }

    def __init__(self):
        super(RoundMob, self).__init__()
        start_pt = (randrange(-50, 0), randrange(WIDTH, WIDTH + 50))[randrange(2)]
        self.frame = 0
        self.yd = randrange(WIDTH / 2)
        self.max_speed = 10
        self.steer_force = 0.2
        self.approach_radius = 100
        self.ch = choice(self.mob_imgs['y'])
        self.image = self.mobsheet.get_image(BLACK, (0, self.ch, 95, 90))
        self.rect = self.image.get_rect()
        self.pos = vec(start_pt, self.yd)
        self.vel = vec(-self.max_speed, 0)
        self.acc = vec(0, 0)
        self.xd = start_pt
        self.radius = 50
        self.shield = 300
        self.next = get_ticks()
        self.shoot_time = self.next
        self.rect.center = self.pos
        self.switch = WIDTH <= start_pt <= WIDTH + 50

    def shoot(self):
        now = get_ticks()
        if now - self.shoot_time > 2500:
            self.shoot_time = now
            x = randrange(2)
            if x == 0:
                MobMissile(self.rect.center).add(game.all_sprites, game.mobs)
            else:
                MobBullet(self.rect.center).add(game.all_sprites, game.mob_bullets)

    def seek_with_approach(self, target):
        self.desired = (target - self.pos)
        dist = self.desired.length()
        self.desired.normalize_ip()
        if dist < self.approach_radius:
            self.desired *= dist / self.approach_radius * self.max_speed
        else:
            self.desired *= self.max_speed
        self.steer = (self.desired - self.vel)
        if self.steer.length() > self.steer_force:
            self.steer.scale_to_length(self.steer_force)
        return self.steer

    def update(self):
        self.shoot()
        now = get_ticks()
        if now - self.next > 500:
            self.next = now
            self.frame += 1
            if self.frame == len(self.mob_imgs['x']):
                self.frame = 0
        self.image = self.mobsheet.get_image(
            BLACK, (self.mob_imgs['x'][self.frame], self.ch,
                    self.mob_imgs['width'][self.frame],
                    self.mob_imgs['height']))
        if self.xd < (WIDTH - 100) // 2:
            self.switch = False
        elif self.xd > (WIDTH + 100) // 2:
            self.switch = True
        if self.switch:
            self.xd -= game.dt // 10
        else:
            self.xd += game.dt // 10
        if (vec(self.xd, self.yd) - self.pos).length():
            self.acc = self.seek_with_approach((self.xd, self.yd))
        self.vel += self.acc
        self.pos += self.vel
        self.rect.center = self.pos


game = Game()
game.start()
while game.running:
    game.run()
    game.pause()
    game.over()
