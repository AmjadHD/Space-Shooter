# Space Shooter game by Amjad Ben Hedhili
from math import cos
from random import choice, random, randrange

import pygame as pg  # type: ignore
from pygame.mixer import music as music_player  # type: ignore
from pygame.math import Vector2 as vec  # type: ignore
from pygame.time import get_ticks  # type: ignore
from pygame.freetype import Font  # type: ignore

from utils import SpriteSheet, write, get_image  # type: ignore
from settings import *  # type: ignore


pg.mixer.pre_init(22050, -16, 1, 512)
pg.init()

# set width and height relative to the device dimensions
info = pg.display.Info()
WIDTH, HEIGHT = info.current_w * 3 // 4, info.current_h * 4 // 5

# the game screen
screen = pg.display.set_mode((WIDTH, HEIGHT), pg.constants.DOUBLEBUF)
# disable alpha for speedier blits
screen.set_alpha(None)
# the game clock
clock = pg.time.Clock()
# set the title of the window
pg.display.set_caption(CAPTION)
# the ship spritesheet
shipsheet = SpriteSheet(osp.join(SPRITESHEETS_FOLDER, "shipsheet.png"))
# set the icon
pg.display.set_icon(shipsheet.get_image((0, 192, 32, 50)))
# restrict the allowed event for faster event handling
pg.event.set_allowed(None)
pg.event.set_allowed((pg.KEYDOWN, pg.KEYUP, pg.QUIT))

title_bar_rect = (0, 0, WIDTH, 30)
mini_ship = shipsheet.get_image_advanced((0, 192, 32, 50), (20, 20))
mini_bomb = SpriteSheet(osp.join(IMAGES_FOLDER, "powerups", "bomb.png")
                        ).get_image_advanced(size=(15, 25))


SOUNDS = {}
for f in glob(osp.join(SOUNDS_FOLDER, "sound_tracks", "**")):
    sound = pg.mixer.Sound(f)
    sound.set_volume(0.3)
    SOUNDS[osp.basename(f).split('.')[0]] = sound

# fonts
font_file = osp.join(GAME_FOLDER, "fonts", "a_Concepto.ttf")
aconcepto100 = Font(font_file, 100)
aconcepto26 = Font(font_file, 26)
aconcepto20 = Font(font_file, 20)
aconcepto14 = Font(font_file, 14)

# delete unused names
del f, font_file, sound, info, Font


# the game
class Game:

    def __init__(self):
        with open("highscore.txt", 'r') as hsf:
            try:
                self.highscore = int(hsf.read())
            except:
                self.highscore = 0
        now = get_ticks()
        # game
        self.is_playing = True

        self.wait_time = now
        self.wait = True
        self.blink_time = now
        self.blink = True
        self.current_track = 0
        self.rand_pos = randrange(40, HEIGHT // 3)
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

    def play(self):
        self.wait_time = get_ticks()
        self.wait = True

        while self.is_playing:
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
        screen.fill(BLACK)
        write(screen, "Space Shooter", (WIDTH // 2, HEIGHT // 4), aconcepto26, WHITE)
        write(screen, "Use Arrows To Move Space Bar To Shoot And B To Bomb",
              (WIDTH // 2, HEIGHT // 2), aconcepto14, WHITE)
        write(screen, f"High Score: {self.highscore}", (WIDTH // 2, HEIGHT * 2 // 3),
              aconcepto26, WHITE)
        pg.display.flip()
        text_rect = aconcepto26.get_rect("press any key")
        text_rect.center = (WIDTH // 2, HEIGHT * 3 // 4)

        while True:
            clock.tick(10)
            self.play_music()
            for event in pg.event.get():
                if event.type == pg.KEYUP:
                    screen.fill(BLACK)
                    pg.display.flip()
                    return
                elif event.type == pg.QUIT:
                    pg.quit()
                    quit()

            now = get_ticks()
            if now - self.blink_time > 1000:
                self.blink_time = now
                if self.blink:
                    self.blink = False
                    aconcepto26.render_to(screen, text_rect, None, WHITE)
                else:
                    self.blink = True
                    screen.fill(BLACK, text_rect)
                pg.display.update(text_rect)

    def over(self):
        ct = self.current_track
        score = self.player.score
        self.__init__()

        self.current_track = ct
        # draw
        screen.fill(BLACK)
        write(screen, "Space Shooter", (WIDTH // 2, HEIGHT // 4), aconcepto26, WHITE)
        write(screen, "Use Arrows To Move Space Bar To Shoot And B To Bomb",
              (WIDTH // 2, HEIGHT // 2), aconcepto14, WHITE)
        pg.display.flip()
        font = aconcepto26
        if score > self.highscore:
            self.highscore = score
            with open("highscore.txt", 'w') as hsf:
                hsf.write(str(self.highscore))
            text = f"New High Score: {self.highscore}"
            text_rect1 = font.get_rect(text)
        else:
            text = "Game Over"
            text_rect1 = font.get_rect(text)
        text_rect1.center = (WIDTH // 2, HEIGHT // 3)
        text_rect2 = font.get_rect("press any key")
        text_rect2.center = (WIDTH // 2, HEIGHT * 3 // 4)
        dirty_rects = (text_rect1, text_rect2)

        while True:
            clock.tick(10)
            self.play_music()
            for event in pg.event.get():
                if event.type == pg.KEYUP and not self.wait:
                    screen.fill(BLACK)
                    pg.display.flip()
                    return
                elif event.type == pg.QUIT:
                    pg.quit()
                    quit()

            now = get_ticks()
            if now - self.wait_time > 1500:
                self.wait = False

            if now - self.blink_time > 1000:
                self.blink_time = now
                if self.blink:
                    self.blink = False
                    font.render_to(screen, text_rect1, text, WHITE)
                    font.render_to(screen, text_rect2, "press any key", WHITE)
                else:
                    self.blink = True
                    screen.fill(BLACK, text_rect1)
                    screen.fill(BLACK, text_rect2)

                pg.display.update(dirty_rects)

    def pause(self):
        while True:
            clock.tick(10)
            self.play_music()
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        music_player.unpause()
                        screen.fill(BLACK)
                        pg.display.flip()
                        return
                elif event.type == pg.QUIT:
                    pg.quit()
                    quit()

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    music_player.pause()
                    write(screen, "paused", (WIDTH // 2, HEIGHT // 2), aconcepto100, WHITE)
                    pg.display.flip()
                    self.pause()
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
                pg.quit()
                quit()

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
        screen.fill(BLACK, title_bar_rect)
        for i in range(player.lives):
            screen.blit(mini_ship, ((WIDTH - 90) + 30 * i, 10))
        for i in range(player.bombs):
            screen.blit(mini_bomb, (110 + 30 * i, 5))
        write(screen, f"Score:{player.score}", (WIDTH // 2, 10), aconcepto20, WHITE)
        write(screen, f"weapon:{player.weapon}/{player.power_level}",
              (WIDTH * 3 // 4, 10), aconcepto14, RED)
        color = RED if player.shield < 20 else (36, 218, 181)
        pg.draw.rect(screen, color, (0, 0, player.shield, 20))
        pg.draw.rect(screen, WHITE, (0, 0, 100, 20), 2)
        if player.shield > 0:
            write(screen, f"{player.shield}%", (50, 10), aconcepto14, RED)

    def get_mobs(self):
        GreyMob.get(self.now)
        RedMob.get(self.now)
        RoundMob.get(self.now)
        EyeLikeMob.get(self.now)
        if len(self.mobs) < 5:
            for i in range(5):
                Asterroid().add(self.all_sprites, self.mobs)

    def handle_collisions(self):
        self.player.hit(pg.sprite.groupcollide(self.mobs, self.bullets, False, True))
        self.player.get_hit_by(pg.sprite.spritecollide(self.player, self.mobs, True))
        self.player.get_hit_by(pg.sprite.spritecollide(self.player, self.mob_bullets, True))
        self.player.get_powerup(pg.sprite.spritecollide(self.player, self.powerups, True))
        self.player.set_power(self.now)

    def play_music(self):
        if music_player.get_busy():
            return
        music_player.load(MUSIC[self.current_track])
        music_player.play(1)
        self.current_track += 1
        if self.current_track == len(MUSIC):
            self.current_track = 0


# the sprites:
class Player(pg.sprite.Sprite):
    """The spaceship sprite"""

    FRAMES = (tuple(shipsheet.get_image_advanced(((0, 32, 67, 99)[i], 192, (32, 32, 30, 30)[i], 50), (40, 63))
                    for i in range(4)),
              tuple(shipsheet.get_image_advanced(((0, 32, 67, 99)[i], 192, (32, 32, 30, 30)[i], 50), (40, 63), horizontally=True)
                    for i in range(4)))

    def __init__(self):
        super(Player, self).__init__()
        self.image = Player.FRAMES[False][0]
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
        self.is_hidden = False
        self.flip = False
        self.open_fire = True
        self.shoot_time = get_ticks()
        self.missile_time = self.shoot_time
        self.power_time = self.shoot_time
        self.strive = self.shoot_time
        self.hide_time = self.shoot_time

    def update(self):
        if self.is_hidden and get_ticks() - self.hide_time > 1500:
            self.bomb()
            self.is_hidden = False
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
        if self.open_fire or key_state[pg.K_SPACE]:
            self.shoot()
        self.image = Player.FRAMES[self.flip][self.frame_nbr]

    def launch_missile(self):
        Missile((self.rect.left, self.rect.centery)).add(game.all_sprites, game.bullets)
        Missile((self.rect.right, self.rect.centery)).add(game.all_sprites, game.bullets)
        Missile((self.rect.centerx, self.rect.top)).add(game.all_sprites, game.bullets)

    def shoot(self):
        if self.is_hidden:
            return

        now = get_ticks()
        if now - self.shoot_time > 250:
            self.shoot_time = now
            if self.weapon == 1:
                SOUNDS["laser1"].play()
                Bullet(self.rect.centerx, self.rect.top).add(
                    game.all_sprites, game.bullets)
            elif self.weapon == 2:
                SOUNDS["laser2"].play()
                Bullet(self.rect.left, self.rect.centery).add(
                    game.all_sprites, game.bullets)
                Bullet(self.rect.right, self.rect.centery).add(
                    game.all_sprites, game.bullets)
            elif self.weapon == 3:
                SOUNDS["laser1"].play()
                SOUNDS["laser2"].play()
                Bullet(self.rect.left, self.rect.centery, -1, 30).add(
                    game.all_sprites, game.bullets)
                Bullet(self.rect.right, self.rect.centery, 1, -30).add(
                    game.all_sprites, game.bullets)
                Bullet(self.rect.centerx, self.rect.top).add(
                    game.all_sprites, game.bullets)
            elif self.weapon == 5:
                SOUNDS["laser1"].play()
                SOUNDS["laser2"].play()
                Bullet(self.rect.left, self.rect.centery).add(
                    game.all_sprites, game.bullets)
                Bullet(self.rect.right, self.rect.centery).add(
                    game.all_sprites, game.bullets)
                Bullet(self.rect.centerx, self.rect.top).add(
                    game.all_sprites, game.bullets)
            elif self.weapon == 6:
                SOUNDS["laser1"].play()
                SOUNDS["laser2"].play()
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
                SOUNDS["laser1"].play()
                SOUNDS["laser2"].play()
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
            SOUNDS["laser1"].play()
            SOUNDS["laser2"].play()
            self.launch_missile()

    def hit(self, objects):
        for object in objects:
            if type(object) is not Asterroid:
                self.score += int(100 - object.radius)
            object.shield -= 16
            if object.shield < 0:
                object.kill()
                mx = max(object.rect.size)
                game.all_sprites.add(Explosion(object.rect.center, (mx, mx)))
                if 0.1 < game.rand < 0.4:
                    Asterroid().add(game.all_sprites, game.mobs)
                elif game.rand > 0.8 and type(object) is RoundMob:
                    Powerup(object.rect.center).add(game.all_sprites, game.powerups)
                elif game.rand > 0.9 and isinstance(object, (GreyMob, RedMob, EyeLikeMob)):
                    Powerup(object.rect.center).add(game.all_sprites, game.powerups)
                elif game.rand > 0.99:
                    Powerup(object.rect.center).add(game.all_sprites, game.powerups)
            else:
                mx = max(object.rect.size) // 2
                game.all_sprites.add(Explosion(object.rect.center, (mx, mx)))

    def get_hit_by(self, objects):
        play_powerdown = SOUNDS["powerdown"].play
        for object in objects:
            play_powerdown()
            self.shield -= object.radius * 2
            if self.weapon == self.power_level:
                self.weapon -= 1
                if self.weapon < 1:
                    self.weapon = 1
            self.power_level -= 1
            if self.power_level < 1:
                self.power_level = 1
            mx = max(object.rect.size) // 2
            game.all_sprites.add(Explosion(object.rect.center, (mx, mx)))
            if self.shield <= 0:
                self.shield = 100
                if self.bombs < 1:
                    self.bombs = 1
                game.all_sprites.add(Explosion(self.rect.center, (150, 150)))
                self.lives -= 1
                if self.lives > 0:
                    # hide
                    self.is_hidden = True
                    self.hide_time = get_ticks()
                    self.rect.center = (2 * WIDTH, 2 * HEIGHT)
                else:
                    self.lives = 0
                    self.kill()
            if not self.lives:
                game.is_playing = False

    def get_powerup(self, powerups):
        for powerup in powerups:
            if powerup.type == "weapon":
                SOUNDS["powerup"].play()
                self.power_level += 1
                if self.power_level <= 7:
                    self.weapon += 1
                self.power_time = get_ticks()
            elif powerup.type == "shield":
                self.shield += randrange(10, 30)
                self.power_time = get_ticks()
                if self.shield >= 100:
                    self.shield = 100
            elif powerup.type == "bomb":
                self.bombs += 1
                if self.bombs < 0:
                    self.bombs = 0
                elif self.bombs > 3:
                    self.bombs = 3

    def set_power(self, now):
        if now - self.power_time < 10000:
            return

        self.power_time = now
        self.power_level -= 1
        if self.power_level < 1:
            self.power_level = 1
        elif self.power_level > 7:
            self.power_level = 7
        if self.weapon > self.power_level:
            self.weapon = self.power_level
        SOUNDS["powerdown"].play()

    def bomb(self):
        SOUNDS["bomb"].play()
        for mob in game.mobs:
            mob.shield -= 50
            if mob.shield <= 0:
                mob.kill()
                mx = max(mob.rect.size)
                game.all_sprites.add(Explosion(mob.rect.center, (mx, mx)))
                if type(mob) is not Asterroid:
                    self.score += 100 - mob.radius


class Bullet(pg.sprite.Sprite):
    """The player's lazer bullets"""

    __slots__ = ("direction",)
    image = get_image(osp.join(IMAGES_FOLDER, "guns", "laser.png"))
    image_copy = image.copy()

    def __init__(self, x, y, direction=0, rot=0):
        super(Bullet, self).__init__()
        self.image = pg.transform.rotate(Bullet.image_copy, rot)
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
    """The player's guided missiles"""

    image = get_image(osp.join(IMAGES_FOLDER, "guns", "missile.png"))

    MAX_SPEED = 18
    radius = 15
    image_copy = image.copy()

    def __init__(self, center):
        super(Missile, self).__init__()
        self.center = center
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
        self.pos += self.vel * game.dt / 10
        if self.pos.x < 0 or self.pos.x > WIDTH or self.pos.y > HEIGHT or self.pos.y < 0:
            self.kill()
        self.rect.center = self.pos


class MobBullet(pg.sprite.Sprite):
    """The mob's bullets"""

    FRAMES = tuple(SpriteSheet(osp.join(SPRITESHEETS_FOLDER, "mobsheet.png")
                               ).get_image_advanced(
        (x, 640, 32, 32), (16, 16)) for x in (0, 32, 64, 128))
    image = FRAMES[0]
    MAX_SPEED = 6
    radius = 5

    def __init__(self, center):
        super(MobBullet, self).__init__()
        self.rect = self.image.get_rect()
        self.pos = vec(center)
        self.vel = (game.player.rect.center - self.pos).normalize() * MobBullet.MAX_SPEED
        self.acc = vec(0, 0)
        self.rect.center = center
        self.center = center
        self.frame_nbr = 0
        self.shield = 5
        self.then = get_ticks()

    def seek(self, target):
        desired = (target - self.pos).normalize() * MobBullet.MAX_SPEED
        steer = desired - self.vel
        if steer.length() > 0.4:
            steer.scale_to_length(0.4)
        return steer

    def update(self):
        now = get_ticks()
        if now - self.then < 20:
            return

        self.then = now
        self.frame_nbr += 1
        if self.frame_nbr == 4:
            self.frame_nbr = 0
        self.acc = vec(0, 0)
        self.vel += self.acc
        if self.vel.length() > MobBullet.MAX_SPEED:
            self.vel.scale_to_length(MobBullet.MAX_SPEED)
        self.pos += self.vel * game.dt / 10
        if not (0 <= self.pos.x <= WIDTH and 0 <= self.pos.y <= HEIGHT):
            self.kill()
        self.image = MobBullet.FRAMES[self.frame_nbr]
        self.rect.center = self.pos


class MobMissile(pg.sprite.Sprite):
    """The mob's guided missiles"""

    FRAMES = tuple(SpriteSheet(osp.join(SPRITESHEETS_FOLDER, "mobsheet.png")
                               ).get_image((x, 0, 16, 40)) for x in (0, 16, 32, 48))
    image = FRAMES[0]
    MAX_SPEED = 6
    radius = 5

    def __init__(self, center):
        super(MobMissile, self).__init__()
        self.rect = self.image.get_rect()
        self.pos = vec(center)
        self.vel = (game.player.rect.center - self.pos).normalize() * MobMissile.MAX_SPEED
        self.acc = vec(0, 0)
        self.rect.center = center
        self.center = center
        self.frame_nbr = 0
        self.shield = 5
        self.then = get_ticks()

    def seek(self, target):
        desired = (target - self.pos).normalize() * MobMissile.MAX_SPEED
        steer = desired - self.vel
        if steer.length() > 0.4:
            steer.scale_to_length(0.4)
        return steer

    def update(self):
        now = get_ticks()
        if now - self.then < 20:
            return

        self.then = now
        self.frame_nbr += 1
        if self.frame_nbr == 4:
            self.frame_nbr = 0
        self.image = MobMissile.FRAMES[self.frame_nbr]
        self.acc = self.seek(game.player.rect.center)
        self.vel += self.acc
        if self.vel.length() > MobMissile.MAX_SPEED:
            self.vel.scale_to_length(MobMissile.MAX_SPEED)
        self.pos += self.vel * game.dt / 10
        if not (0 <= self.pos.x <= WIDTH and 0 <= self.pos.y <= HEIGHT):
            self.kill()
        self.rect.center = self.pos


class Asterroid(pg.sprite.Sprite):
    """The rocks floating in the space"""

    METEORS = tuple(get_image(f, WHITE) for f in glob(osp.join(IMAGES_FOLDER, "meteors", "*png")))

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
        if now - self.rot_time < 50:
            return

        self.rot_time = now
        self.rotation = (self.rotation + self.rot_speed) % 360
        center = self.rect.center
        self.image = pg.transform.rotate(self.image_copy, self.rotation)
        self.rect = self.image.get_rect()
        self.rect.center = center

    def update(self):
        self.rotate()
        self.rect.x += self.speedx * game.dt / 10
        self.rect.y += self.speedy * game.dt / 10
        if self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:
            if self.alive():
                self.rect.x = randrange(WIDTH - self.rect.width)
                self.rect.y = randrange(-100, -40)
                self.speedx = randrange(-6, 6)
                self.speedy = randrange(4, 6)


class Explosion(pg.sprite.Sprite):
    """A class for all types of explosions"""

    explosion_sheet = SpriteSheet(osp.join(SPRITESHEETS_FOLDER, "explsheet.png"))
    METADATA = {
        "x": tuple(j * 100 for i in range(8) for j in range(9)),
        "y": tuple(i * 100 for i in range(8) for j in range(9)),
        "width": 100,
        "height": 100
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
        if now - self.then < 1:
            return

        self.then = now
        self.frame_nbr += 6
        if self.frame_nbr == len(Explosion.METADATA["x"]):
            self.kill()
            return
        center = self.rect.center
        self.image = Explosion.explosion_sheet.get_image_advanced((
            Explosion.METADATA["x"][self.frame_nbr],
            Explosion.METADATA["y"][self.frame_nbr],
            100, 100
        ), self.size)
        self.rect = self.image.get_rect()
        self.rect.center = center


class Powerup(pg.sprite.Sprite):
    """All the powerups: shield, weapon..."""

    POWERUPS = {osp.basename(f).split(".")[0]: get_image(f)
                for f in glob(osp.join(IMAGES_FOLDER, "powerups", "*png"))}

    def __init__(self, center):
        super(Powerup, self).__init__()
        self.type = ("bomb", "shield", "weapon")[randrange(3)]
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
    """elongated grey alienship"""

    image = SpriteSheet(osp.join(IMAGES_FOLDER, "mobs", "greymob.png")
                        ).get_image_advanced(size=(61, 92))
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
        desired = target - self.pos
        dist = desired.length()
        desired.normalize_ip()
        if dist < GreyMob.APPROACH_RADIUS:
            desired *= dist / GreyMob.APPROACH_RADIUS * GreyMob.MAX_SPEED
        else:
            desired *= GreyMob.MAX_SPEED
        steer = desired - self.vel
        if steer.length() > GreyMob.STEER_FORCE:
            steer.scale_to_length(GreyMob.STEER_FORCE)
        return steer

    @classmethod
    def get(cls, now):
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
        self.pos += self.vel * game.dt / 10
        self.rect.center = self.pos


class RedMob(pg.sprite.Sprite):
    """The elongted red alienship"""
    image = SpriteSheet(osp.join(IMAGES_FOLDER, "mobs", "redmob.png")
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
        self.acc = vec(0, 10)
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
    def get(cls, now):
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
            self.acc.x = cos(self.c) * RedMob.MAX_SPEED - 10
        if self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:
            self.kill()
            return
        if now - self.dtime > 2000:
            self.dtime = now
            self.right = not self.right
        self.vel += self.acc
        if self.vel.length() > RedMob.MAX_SPEED:
            self.vel.scale_to_length(RedMob.MAX_SPEED)
        self.pos += self.vel * game.dt / 10
        self.rect.center = self.pos


class EyeLikeMob(pg.sprite.Sprite):
    """The eye-like alienship"""

    FRAMES = tuple(SpriteSheet(osp.join(SPRITESHEETS_FOLDER, "eyelike_mobsheet.png")
                               ).get_image(((0, 31, 63, 95, 127, 175, 223, 270)[i],
                                            0, (31, 32, 32, 32, 48, 48, 48, 48)[i], 80))
                   for i in range(8))
    image = FRAMES[0]
    count = 0
    duration = get_ticks()
    next_time = duration
    its_time = True
    radius = 50

    def __init__(self, y):
        super(EyeLikeMob, self).__init__()
        self.frame_nbr = 0
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH + 40, y)
        self.shield = 12
        self.then = get_ticks()
        self.shoot_time = self.then
        self.switch = False
        EyeLikeMob.count += 1

    def shoot(self, now):
        if now - self.shoot_time > 3500:
            self.shoot_time = now
            MobBullet(self.rect.center).add(game.all_sprites, game.mob_bullets)

    @classmethod
    def get(cls, now):
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
        self.rect.x -= game.dt / 3


class RoundMob(pg.sprite.Sprite):
    """The round alienship"""

    FRAMES = tuple(tuple(SpriteSheet(osp.join(SPRITESHEETS_FOLDER, "mobsheet.png")
                                     ).get_image(
        ((0, 95, 190, 285, 385, 480, 575)[i],
         y,
         (95, 95, 95, 100, 95, 95, 95)[i],
         90)) for i in range(7))
        for y in (45, 270, 496, 718))
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
        self.y = randrange(100, HEIGHT // 2)
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
        desired = target - self.pos
        dist = desired.length()
        desired.normalize_ip()
        if dist < RoundMob.APPROACH_RADIUS:
            desired *= dist / RoundMob.APPROACH_RADIUS * RoundMob.MAX_SPEED
        else:
            desired *= RoundMob.MAX_SPEED
        steer = desired - self.vel
        if steer.length() > RoundMob.STEER_FORCE:
            steer.scale_to_length(RoundMob.STEER_FORCE)
        return steer

    @classmethod
    def get(cls, now):
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
            self.x -= game.dt / 10
        else:
            self.x += game.dt / 10
        if (vec(self.x, self.y) - self.pos).length():
            self.acc = self.seek_with_approach((self.x, self.y))
        self.vel += self.acc
        self.pos += self.vel
        self.rect.center = self.pos


game = Game()
game.start()
while True:
    game.play()
    game.over()
