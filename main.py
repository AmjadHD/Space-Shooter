# Space Shooter game by Amjad Ben Hedhili
from math import cos
from random import choice, random, randrange
from glob import glob
from os.path import join

import pygame as pg
from pygame.mixer import music as music_player
from pygame.math import Vector2 as vec
from pygame.time import get_ticks
from pygame.freetype import SysFont

from utils import SpriteSheet, write, get_image
from settings import *


pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT), pg.constants.DOUBLEBUF)
screen.set_alpha(None)
clock = pg.time.Clock()
pg.display.set_caption(CAPTION)
shipsheet = SpriteSheet(join(SPRITESHEETS_FOLDER, 'shipsheet.png'))
pg.display.set_icon(shipsheet.get_image((0, 192, 32, 50)))
pg.event.set_allowed((pg.KEYDOWN, pg.KEYUP, pg.QUIT))

title_bar_rect = (0, 0, WIDTH, 30)
mini_ship = shipsheet.get_image_advanced((0, 192, 32, 50), (20, 20))
mini_bomb = SpriteSheet(join(IMAGES_FOLDER, 'powerups', 'spaceMissiles_006.png')
                        ).get_image_advanced(size=(15, 25))
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
        with open("highscore.txt", "r") as hsf:
            try:
                self.highscore = int(hsf.read())
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
        self.rand_pos = randrange(40, HEIGHT // 3)
        self.new_highscore = False
        self.restart = True
        self.player = Player()

        # grey mob
        GreyMob.duration = now
        GreyMob.next_time = now
        GreyMob.its_time = True
        GreyMob.count = 0
        # red mob
        RedMob.duration = now
        RedMob.next_time = now
        RedMob.its_time = False
        RedMob.count = 0
        # eye-like mob
        EyeLikeMob.duration = now
        EyeLikeMob.next_time = now
        EyeLikeMob.count = 0
        # round mob
        RoundMob.next_time = now

        # groups
        self.all_sprites = pg.sprite.RenderUpdates(self.player)
        self.mobs = pg.sprite.Group()
        self.powerups = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.mob_bullets = pg.sprite.Group()

    def run(self):
        self.dt = clock.tick(FPS) // 2
        self.now = get_ticks()
        self.rand = random()

        # play music
        self.play_music()

        # handle events
        self.handle_events()

        # collisions:
        self.handle_collisions()

        # mobs stuff
        self.get_mobs()

        # draw and update everything on the screen
        self.draw_and_update()

    def start(self):
        while True:
            clock.tick(15)
            self.play_music()
            for event in pg.event.get():
                if event.type == pg.KEYUP:
                    screen.fill(BLACK)
                    pg.display.flip()
                    return
                elif event.type == pg.QUIT:
                    pg.quit()
                    quit()

            screen.fill(BLACK)
            write(screen, "Space Shooter", (WIDTH / 2, HEIGHT / 4), aconcepto26, WHITE)
            write(screen, 'Use Arrows To Move Space Bar To Shoot And B To Bomb',
                  (WIDTH / 2, HEIGHT / 2), aconcepto14, WHITE)
            now = get_ticks()
            if now - self.blink_time > 1000:
                self.blink_time = now
                self.blink = not self.blink
            write(screen, f'High Score: {self.highscore}', (WIDTH // 2, HEIGHT * 2 // 3),
                  aconcepto26, WHITE)
            if self.blink:
                write(screen, 'press any key', (WIDTH // 2, HEIGHT * 3 // 4),
                      aconcepto26, WHITE)

            pg.display.flip()

    def over(self):
        while self.game_over:
            clock.tick(15)
            self.play_music()
            for event in pg.event.get():
                if event.type == pg.KEYUP and not self.wait:
                    self.game_over = False
                    screen.fill(BLACK)
                    pg.display.flip()
                    return
                elif event.type == pg.QUIT:
                    pg.quit()
                    quit()

            now = get_ticks()
            if now - self.wait_time > 1500:
                self.wait = False
            # initialisation:
            if self.restart:
                ct = self.current_track
                score = self.player.score
                self.__init__()
                if score > self.highscore:
                    self.new_highscore = True
                    self.highscore = score
                    with open("highscore.txt", "w") as hsf:
                        hsf.write(str(self.highscore))

                self.game_over = True
                self.restart = False
                self.current_track = ct
            # draw
            screen.fill(BLACK)
            write(screen, "Space Shooter", (WIDTH // 2, HEIGHT // 4), aconcepto26, WHITE)
            write(screen, 'Use Arrows To Move Space Bar To Shoot And B To Bomb',
                  (WIDTH / 2, HEIGHT / 2), aconcepto14, WHITE)
            if now - self.blink_time > 1000:
                self.blink_time = now
                self.blink = not self.blink
            if self.blink:
                if self.new_highscore:
                    write(screen, f'New High Score: {self.highscore}',
                          (WIDTH // 2, HEIGHT // 3), aconcepto26, WHITE)
                else:
                    write(screen, 'Game Over', (WIDTH // 2, HEIGHT // 3),
                          aconcepto26, WHITE)
                write(screen, 'press any key', (WIDTH // 2, HEIGHT * 3 // 4),
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
                        screen.fill(BLACK)
                        pg.display.flip()
                        return
                elif event.type == pg.QUIT:
                    pg.quit()
                    quit()
            write(screen, 'paused', (WIDTH // 2, HEIGHT // 2), aconcepto100, WHITE)
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
                    self.player.open_fire = not self.player.open_fire
                elif event.key == pg.K_b and self.player.bombs > 0:
                    self.player.bombs -= 1
                    self.player.bomb()
            elif event.type == pg.QUIT:
                self.running = False

    def draw_and_update(self):
        self.all_sprites.clear(screen, lambda surf, rect: surf.fill(BLACK, rect))
        self.all_sprites.update()
        # draw
        dirty_rects = self.all_sprites.draw(screen)
        self.draw_title_bar()
        dirty_rects.append(title_bar_rect)
        # update
        pg.display.update(dirty_rects)

    def draw_title_bar(self):
        player = self.player
        screen_blit = screen.blit
        screen.fill(BLACK, title_bar_rect)
        for i in range(player.lives):
            screen_blit(mini_ship, ((WIDTH - 90) + 30 * i, 10))
        for i in range(player.bombs):
            screen_blit(mini_bomb, (110 + 30 * i, 5))
        write(screen, f'Score:{player.score}', (WIDTH // 2, 10), aconcepto20, WHITE)
        write(screen, f'weapon:{player.weapon}/{player.power_level}',
              (WIDTH * 3 // 4, 10), aconcepto14, RED)
        color = RED if player.shield < 20 else (36, 218, 181)
        pg.draw.rect(screen, color, (0, 0, player.shield, 20))
        pg.draw.rect(screen, WHITE, (0, 0, 100, 20), 2)
        if player.shield > 0:
            write(screen, f'{player.shield}%', (50, 10), aconcepto14, RED)

    def get_mobs(self):
        GreyMob.get(self, self.now)
        RedMob.get(self, self.now)
        RoundMob.get(self, self.now)
        EyeLikeMob.get(self, self.now)
        if len(self.mobs) < 5:
            for i in range(7):
                Asterroid().add(self.all_sprites, self.mobs)

    def handle_collisions(self):
        for mob in pg.sprite.groupcollide(self.mobs, self.bullets, False, True):
            self.player.hit(mob)
        for mob in pg.sprite.spritecollide(self.player, self.mobs, True):
            self.player.get_hit(mob)
        for powerup in pg.sprite.spritecollide(self.player, self.powerups, True):
            self.player.get_powerup(powerup)
        for mob_bullet in pg.sprite.spritecollide(self.player, self.mob_bullets, True):
            self.player.get_hit(mob_bullet)
        self.player.set_power(self.now)

    def play_music(self):
        if not music_player.get_busy():
            music_player.load(MUSIC[self.current_track])
            music_player.play(1)
            self.current_track += 1
            if self.current_track == len(MUSIC):
                self.current_track = 0
        if self.paused:
            music_player.pause()
        else:
            music_player.unpause()


# the sprites:
class Player(pg.sprite.Sprite):
    '''The spaceship sprite'''

    FRAMES = tuple((shipsheet.get_image_advanced(((0, 32, 67, 99)[i], 192,
                                                  (32, 32, 30, 30)[i], 50), (40, 63)),
                    shipsheet.get_image_advanced(((0, 32, 67, 99)[i], 192,
                                                  (32, 32, 30, 30)[i], 50), (40, 63), horizontally=True)
                    ) for i in range(4))

    def __init__(self):
        super(Player, self).__init__()
        self.image = Player.FRAMES[0][False]
        self.rect = self.image.get_rect()
        self.rect.bottom = HEIGHT - 10
        self.rect.centerx = WIDTH // 2
        self.radius = 10
        self.frame_nbr = 0
        self.lives = 3
        self.shield = 100
        self.score = 0
        self.power_level = 1
        self.weapon = 1
        self.bombs = 1
        self.hidden = False
        self.flip = False
        self.open_fire = True
        self.shoot_time = get_ticks()
        self.missile_time = self.shoot_time
        self.power_time = self.shoot_time
        self.strive = self.shoot_time
        self.hide_time = self.shoot_time

    def update(self):
        if self.hidden and get_ticks() - self.hide_time > 1500:
            self.bomb()
            self.hidden = False
            self.rect.centerx = WIDTH // 2
            self.rect.bottom = HEIGHT - 10
        key_state = pg.key.get_pressed()
        step = game.dt
        if key_state[pg.K_LEFT] or key_state[pg.K_RIGHT]:
            if key_state[pg.K_UP] or key_state[pg.K_DOWN]:
                step = game.dt / 1.414
            if key_state[pg.K_LEFT]:
                self.rect.x -= step
                if self.rect.left <= 0:
                    self.rect.left = 0
                self.flip = False
            elif key_state[pg.K_RIGHT]:
                self.rect.x += step
                if self.rect.right >= WIDTH:
                    self.rect.right = WIDTH
                self.flip = True
            now = get_ticks()
            if now - self.strive > 100:
                self.strive = now
                self.frame_nbr += 1
                if self.frame_nbr > 3:
                    self.frame_nbr = 3
        else:
            self.frame_nbr = 0
        if key_state[pg.K_UP]:
            self.rect.y -= step
            if self.rect.top <= 0:
                self.rect.top = 0
        elif key_state[pg.K_DOWN]:
            self.rect.y += step
            if HEIGHT <= self.rect.bottom < HEIGHT + 100:
                self.rect.bottom = HEIGHT
        if key_state[pg.K_SPACE] or self.open_fire:
            self.shoot()
        self.image = Player.FRAMES[self.frame_nbr][self.flip]

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

    def set_power(self, now):
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


class Bullet(pg.sprite.Sprite):
    '''The player's lazer bullets'''

    __slots__ = ("direction",)
    image = get_image(join(IMAGES_FOLDER, 'guns', 'laser.png'))

    def __init__(self, x, y, direction=0, rot=0):
        super(Bullet, self).__init__()
        self.image = pg.transform.rotate(Bullet.image.copy(), rot)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.direction = direction

    def update(self):
        self.rect.y -= 2 * game.dt
        self.rect.x += self.direction * game.dt
        if self.rect.bottom < 0 or self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()


class Missile(pg.sprite.Sprite):
    '''The player's guided missiles'''

    image = get_image(join(IMAGES_FOLDER, 'guns', 'missile.png'))

    MAX_SPEED = 18
    radius = 15

    def __init__(self, center):
        super(Missile, self).__init__()
        self.center = center
        self.image_copy = self.image.copy()
        self.rect = self.image.get_rect()
        self.target = choice(game.mobs.sprites())
        self.pos = vec(self.center)
        self.vel = vec(0, -Missile.MAX_SPEED / 2)
        self.acc = vec(0, 0)
        self.rect.center = self.pos
        self.shield = 5

    def seek(self, target):
        desired = (target - self.pos).normalize() * Missile.MAX_SPEED
        steer = desired - self.vel
        if steer.length() > 1:
            steer.scale_to_length(1)
        return steer

    def update(self):
        self.acc = self.seek(self.target.rect.center)
        if not self.target.alive() or type(self.target) is Asterroid:
            self.target = choice(game.mobs.sprites())
        self.vel += self.acc
        self.normal = vec(0, self.rect.centery)
        self.image = pg.transform.rotate(self.image_copy,
                                         self.vel.angle_to(self.normal) + 180)
        if self.vel.length() > Missile.MAX_SPEED:
            self.vel.scale_to_length(Missile.MAX_SPEED)
        self.pos += self.vel
        if self.pos.x < 0 or self.pos.x > WIDTH or self.pos.y > HEIGHT or self.pos.y < 0:
            self.kill()
        self.rect.center = self.pos


class MobBullet(pg.sprite.Sprite):
    '''The mob's bullets'''

    FRAMES = tuple(SpriteSheet(join(SPRITESHEETS_FOLDER, 'mobsheet.png')
                               ).get_image_advanced(
        ((0, 32, 64, 128)[i], 640, 32, 32), (16, 16)) for i in range(4))
    image = FRAMES[0]
    MAX_SPEED = 6
    radius = 5

    def __init__(self, center):
        super(MobBullet, self).__init__()
        self.rect = self.image.get_rect()
        self.pos = vec(center)
        self.vel = (
            game.player.rect.center - self.pos).normalize() * 1.5 * MobBullet.MAX_SPEED
        self.acc = vec(0, 0)
        self.rect.center = center
        self.center = center
        self.frame_nbr = 0
        self.shield = 5
        self.then = get_ticks()

    def seek(self, target):
        desired = (target - self.pos).normalize() * MobBullet.MAX_SPEED
        steer = (desired - self.vel)
        if steer.length() > 0.4:
            steer.scale_to_length(0.4)
        return steer

    def update(self):
        now = get_ticks()
        if now - self.then > 20:
            self.then = now
            self.frame_nbr += 1
            if self.frame_nbr == 4:
                self.frame_nbr = 0
            self.acc = vec(0, 0)
            self.vel += self.acc
            if self.vel.length() > MobBullet.MAX_SPEED:
                self.vel.scale_to_length(MobBullet.MAX_SPEED)
            self.pos += self.vel
            if not (0 <= self.pos.x <= WIDTH and 0 <= self.pos.y <= HEIGHT):
                self.kill()
            self.image = MobBullet.FRAMES[self.frame_nbr]
            self.rect.center = self.pos


class MobMissile(pg.sprite.Sprite):
    '''The mob's guided missiles'''

    FRAMES = tuple(SpriteSheet(join(SPRITESHEETS_FOLDER, 'mobsheet.png')
                               ).get_image(((0, 16, 32, 48)[i], 0, 16, 40)) for i in range(4))
    image = FRAMES[0]
    MAX_SPEED = 6
    radius = 5

    def __init__(self, center):
        super(MobMissile, self).__init__()
        self.rect = self.image.get_rect()
        self.pos = vec(center)
        self.vel = (
            game.player.rect.center - self.pos).normalize() * 1.5 * MobMissile.MAX_SPEED
        self.acc = vec(0, 0)
        self.rect.center = center
        self.center = center
        self.frame_nbr = 0
        self.shield = 5
        self.then = get_ticks()

    def seek(self, target):
        desired = (target - self.pos).normalize() * MobMissile.MAX_SPEED
        steer = (desired - self.vel)
        if steer.length() > 0.4:
            steer.scale_to_length(0.4)
        return steer

    def update(self):
        now = get_ticks()
        if now - self.then > 20:
            self.then = now
            self.frame_nbr += 1
            if self.frame_nbr == 4:
                self.frame_nbr = 0
            self.image = MobMissile.FRAMES[self.frame_nbr]
            self.acc = self.seek(game.player.rect.center)
            self.vel += self.acc
            if self.vel.length() > MobMissile.MAX_SPEED:
                self.vel.scale_to_length(MobMissile.MAX_SPEED)
            self.pos += self.vel
            if not (0 <= self.pos.x <= WIDTH and 0 <= self.pos.y <= HEIGHT):
                self.kill()
            self.rect.center = self.pos


class Asterroid(pg.sprite.Sprite):
    '''The rocks floating in the space'''

    METEORS = tuple(get_image(f, WHITE) for f in glob(join(IMAGES_FOLDER, 'meteors', '*png')))

    def __init__(self):
        super(Asterroid, self).__init__()
        self.image = choice(Asterroid.METEORS)
        self.rect = self.image.get_rect()
        self.rect.bottom = 0
        self.rect.x = randrange(WIDTH - self.rect.width)
        self.rect.y = randrange(-200, -100)
        self.image_copy = self.image.copy()
        self.rotation = 0
        self.rot_speed = randrange(-8, 8)
        self.rot_time = get_ticks()
        self.speedx = randrange(-6, 6)
        self.speedy = randrange(4, 6)
        self.radius = self.rect.width * 0.85 // 2
        self.shield = self.radius // 2

    def rotate(self):
        now = get_ticks()
        if now - self.rot_time > 50:
            self.rot_time = now
            self.rotation = (self.rotation + self.rot_speed) % 360
            center = self.rect.center
            self.image = pg.transform.rotate(self.image_copy, self.rotation)
            self.rect = self.image.get_rect()
            self.rect.center = center

    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:
            if self.alive():
                self.rect.x = randrange(WIDTH - self.rect.width)
                self.rect.y = randrange(-100, -40)
                self.speedx = randrange(-6, 6)
                self.speedy = randrange(4, 6)


class Explosion(pg.sprite.Sprite):
    '''A class for all types of explosions'''

    explosion_sheet = SpriteSheet(join(SPRITESHEETS_FOLDER, 'explsheet.png'))
    EXPLOSION_IMGS = {
        'x': tuple(j * 100 for i in range(8) for j in range(9)),
        'y': tuple(i * 100 for i in range(8) for j in range(9)),
        'width': 100,
        'height': 100
    }

    def __init__(self, center, size):
        super(Explosion, self).__init__()
        self.image = self.explosion_sheet.get_image_advanced((0, 0, 100, 100), size)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.size = size
        self.frame_nbr = 0
        self.then = get_ticks()

    def update(self):
        now = get_ticks()
        if now - self.then > 1:
            self.then = now
            self.frame_nbr += 6
            if self.frame_nbr == len(Explosion.EXPLOSION_IMGS['x']):
                self.kill()
                return
            center = self.rect.center
            self.image = Explosion.explosion_sheet.get_image_advanced((
                Explosion.EXPLOSION_IMGS['x'][self.frame_nbr],
                Explosion.EXPLOSION_IMGS['y'][self.frame_nbr],
                Explosion.EXPLOSION_IMGS['width'],
                Explosion.EXPLOSION_IMGS['height']
            ), self.size)
            self.rect = self.image.get_rect()
            self.rect.center = center


class Powerup(pg.sprite.Sprite):
    '''All the POWERUPS: shield, weapon...'''

    POWERUPS = tuple(get_image(f) for f in glob(join(IMAGES_FOLDER, 'powerups', '*png')))

    def __init__(self, center):
        super(Powerup, self).__init__()
        self.type = randrange(3)
        self.image = self.POWERUPS[self.type]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.centery = center[1]
        self.up = True

    def update(self):
        if self.rect.centery < self.centery - 50:
            self.up = False
        if self.rect.top > HEIGHT:
            self.kill()
            return
        if self.up:
            self.rect.y -= game.dt / 2
        else:
            self.rect.y += game.dt / 4


class GreyMob(pg.sprite.Sprite):
    '''elongated grey alienship'''
    image = SpriteSheet(join(IMAGES_FOLDER, "mobs", 'greymob.png')
                        ).get_image_advanced(size=(100, 100))
    count = 0
    duration = get_ticks()
    next_time = duration
    its_time = True
    MAX_SPEED = 10
    APPROACH_RADIUS = 100
    STEER_FORCE = 2
    radius = 50

    def __init__(self, x, y):
        super(GreyMob, self).__init__()
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y + 200
        self.pos = vec(x, y)
        self.vel = vec(0, GreyMob.MAX_SPEED)
        self.acc = vec(0, 0)
        self.rect.center = self.pos
        self.shield = 17
        self.right = True
        now = get_ticks()
        self.shoot_time = now
        self.dtime = now
        GreyMob.count += 1

    def shoot(self, now):
        if now - self.shoot_time > 3000:
            self.shoot_time = now
            MobBullet(self.rect.center).add(game.all_sprites, game.mob_bullets)

    def seek_with_approach(self, target):
        desired = (target - self.pos)
        dist = desired.length()
        desired.normalize_ip()
        if dist < GreyMob.APPROACH_RADIUS:
            desired *= dist / GreyMob.APPROACH_RADIUS * GreyMob.MAX_SPEED
        else:
            desired *= GreyMob.MAX_SPEED
        steer = (desired - self.vel)
        if steer.length() > GreyMob.STEER_FORCE:
            steer.scale_to_length(GreyMob.STEER_FORCE)
        return steer

    @classmethod
    def get(cls, game, now):
        if now - cls.duration > 10000:
            cls.duration = now
            cls.its_time = True
        if now - cls.next_time > 500 and cls.its_time:
            cls.next_time = now
            cls(200, -50).add(game.all_sprites, game.mobs)
            if cls.count > 5:
                cls.count = 0
                cls.its_time = False

    def update(self):
        now = get_ticks()
        self.shoot(now)
        if not ((self.x, self.y) - self.pos).length() == 0:
            self.acc = self.seek_with_approach((self.x, self.y))
        if now - self.dtime > 2000:
            self.dtime = now
            self.y += 400
            if self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:
                self.kill()
                return
            if self.right:
                self.x += 100
                self.right = False
            else:
                self.x -= 100
                self.right = True
        self.vel += self.acc
        if self.vel.length() > GreyMob.MAX_SPEED:
            self.vel.scale_to_length(GreyMob.MAX_SPEED)
        self.pos += self.vel
        self.rect.center = self.pos


class RedMob(pg.sprite.Sprite):
    '''The elongted red alienship'''
    image = SpriteSheet(join(IMAGES_FOLDER, "mobs", 'redmob.png')
                        ).get_image_advanced(size=(58, 100))
    count = 0
    duration = get_ticks()
    next_time = duration
    its_time = False
    MAX_SPEED = 10
    radius = 40

    def __init__(self, x, y):
        super(RedMob, self).__init__()
        self.rect = self.image.get_rect()
        self.pos = vec(x, y)
        self.vel = vec(0, RedMob.MAX_SPEED)
        self.acc = vec(0, 0)
        self.rect.center = self.pos
        self.shield = 10
        self.right = True
        self.c = 0
        now = get_ticks()
        self.shoot_time = now
        self.dtime = now
        self.then = now
        RedMob.count += 1

    def shoot(self, now):
        if now - self.shoot_time > 3000:
            self.shoot_time = now
            MobBullet(self.rect.center).add(game.all_sprites, game.mob_bullets)

    @classmethod
    def get(cls, game, now):
        if now - cls.duration > 8000:
            cls.duration = now
            cls.its_time = True
        if now - cls.next_time > 200 and cls.its_time:
            cls.next_time = now
            cls(500, -200).add(game.all_sprites, game.mobs)
            if cls.count > 5:
                cls.count = 0
                cls.its_time = False

    def update(self):
        now = get_ticks()
        self.shoot(now)
        if now - self.then > 300:
            self.then = now
            self.c = (self.c + 5) % 360
        self.acc = vec(cos(self.c) * RedMob.MAX_SPEED - 10, 10)
        if self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:
            self.kill()
            return
        if now - self.dtime > 2000:
            self.dtime = now
            if self.right:
                self.right = False
            else:
                self.right = True
        self.vel += self.acc
        if self.vel.length() > RedMob.MAX_SPEED:
            self.vel.scale_to_length(RedMob.MAX_SPEED)
        self.pos += self.vel
        self.rect.center = self.pos


class EyeLikeMob(pg.sprite.Sprite):
    '''The eye-like alienship'''

    FRAMES = tuple(SpriteSheet(join(SPRITESHEETS_FOLDER, 'eyelike_mobsheet.png')
                               ).get_image(((0, 31, 63, 95, 127, 175, 223, 270)[i],
                                            0, (31, 32, 32, 32, 48, 48, 48, 48)[i], 80))
                   for i in range(8))
    image = FRAMES[0]
    count = 0
    duration = get_ticks()
    next_time = duration
    its_time = True

    def __init__(self, y):
        super(EyeLikeMob, self).__init__()
        self.frame_nbr = 0
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH + 40, y)
        self.radius = 50
        self.shield = 12
        self.then = get_ticks()
        self.shoot_time = self.then
        self.switch = False
        EyeLikeMob.count += 1

    def shoot(self, now):
        if now - self.shoot_time > 4000:
            self.shoot_time = now
            MobBullet(self.rect.center).add(game.all_sprites, game.mob_bullets)

    @classmethod
    def get(cls, game, now):
        if now - cls.next_time > 12000:
            cls.next_time = now
            if game.rand < 0.9:
                cls.count = 0
                game.rand_pos = randrange(40, HEIGHT // 3)
        if now - cls.duration > 500 and cls.count < 12:
            cls.duration = now
            cls(game.rand_pos).add(game.all_sprites, game.mobs)

    def update(self):
        now = get_ticks()
        self.shoot(now)
        if now - self.then > 500:
            self.then = now
            self.frame_nbr += 1
            if self.frame_nbr == 8:
                self.frame_nbr = 0
            self.image = EyeLikeMob.FRAMES[self.frame_nbr]
        if self.rect.right < 0:
            self.kill()
            return
        self.rect.x -= 4


class RoundMob(pg.sprite.Sprite):
    '''The round alienship'''

    FRAMES = tuple(tuple(SpriteSheet(join(SPRITESHEETS_FOLDER, 'mobsheet.png')
                                     ).get_image(
        ((0, 95, 190, 285, 385, 480, 575)[frame],
         rand,
         (95, 95, 95, 100, 95, 95, 95)[frame],
         90)) for frame in range(7))
        for rand in (45, 270, 496, 718))
    next_time = get_ticks()
    MAX_SPEED = 10
    STEER_FORCE = 0.2
    APPROACH_RADIUS = 100
    radius = 50

    def __init__(self):
        super(RoundMob, self).__init__()
        start_pt = (-50, WIDTH + 50)[randrange(2)]
        self.ch = randrange(4)
        self.x = start_pt
        self.y = randrange(WIDTH // 2)
        self.image = RoundMob.FRAMES[self.ch][0]
        self.rect = self.image.get_rect()
        self.pos = vec(start_pt, self.y)
        self.vel = vec(-RoundMob.MAX_SPEED, 0)
        self.acc = vec(0, 0)
        self.rect.center = self.pos
        self.frame_nbr = 0
        self.shield = 300
        self.then = get_ticks()
        self.shoot_time = self.then
        self.switch = start_pt == WIDTH + 50

    def shoot(self, now):
        if now - self.shoot_time > 2500:
            self.shoot_time = now
            if randrange(2) == 0:
                MobMissile(self.rect.center).add(game.all_sprites, game.mobs)
            else:
                MobBullet(self.rect.center).add(game.all_sprites, game.mob_bullets)

    def seek_with_approach(self, target):
        desired = (target - self.pos)
        dist = desired.length()
        desired.normalize_ip()
        if dist < RoundMob.APPROACH_RADIUS:
            desired *= dist / RoundMob.APPROACH_RADIUS * RoundMob.MAX_SPEED
        else:
            desired *= RoundMob.MAX_SPEED
        steer = (desired - self.vel)
        if steer.length() > RoundMob.STEER_FORCE:
            steer.scale_to_length(RoundMob.STEER_FORCE)
        return steer

    @classmethod
    def get(cls, game, now):
        if now - cls.next_time > 6000:
            cls.next_time = now
            if game.rand > 0.6:
                cls().add(game.all_sprites, game.mobs)

    def update(self):
        now = get_ticks()
        self.shoot(now)
        if now - self.then > 500:
            self.then = now
            self.frame_nbr += 1
            if self.frame_nbr == 7:
                self.frame_nbr = 0
            self.image = RoundMob.FRAMES[self.ch][self.frame_nbr]
        if self.x < (WIDTH - 100) // 2:
            self.switch = False
        elif self.x > (WIDTH + 100) // 2:
            self.switch = True
        if self.switch:
            self.x -= game.dt // 10
        else:
            self.x += game.dt // 10
        if (vec(self.x, self.y) - self.pos).length():
            self.acc = self.seek_with_approach((self.x, self.y))
        self.vel += self.acc
        self.pos += self.vel
        self.rect.center = self.pos


game = Game()
game.start()
while game.running:
    game.run()
    game.pause()
    game.over()
