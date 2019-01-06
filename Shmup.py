# Space Shooter game by Ben Hedhili Amjad:
from math import cos
from random import choice, randint, random, randrange
from settings import *

# functions:

def text(screen, msg, center, font, color):
    '''A function that draws a text on the screen'''
    textsurf = font.render(msg, False, color, 5)
    text_pos = textsurf.get_rect()
    text_pos.center = center
    screen.blit(textsurf, text_pos)


def get_hit(iterator):
    global wait, wait_time, game_over, expl
    pg.mixer.Sound(SOUNDS[4]).play()
    new_asterroid()
    player.shield -= iterator.radius * 2
    if player.weapon == player.pwr_level:
        player.weapon -= 1
        if player.weapon < 1:
            player.weapon = 1
    player.pwr_level -= 1
    if not player.hidden:
        mx = max(iterator.rect.width // 2, iterator.rect.height // 2)
        all_sprites.add(Explosion(iterator.rect.center, (mx, mx)))
    if player.shield <= 0:
        player.shield = 100
        if player.bombs < 1:
            player.bombs = 1
        all_sprites.add(Explosion(player.rect.center, (150, 150)))
        player.lives -= 1
        if player.lives > 0:
            player.hide()
        else:
            player.lives = 0
            player.kill()
    if not player.lives and not expl.alive():
        game_over = True
        wait_time = now
        wait = True


def music_player():
    pg.init()
    global msc
    if not pg.mixer.music.get_busy():
        pg.mixer.music.load(MUSIC[msc])
        pg.mixer.music.play(1)
        msc += 1
    if msc == len(MUSIC):
        msc = 0
    if paused:
        pg.mixer.music.pause()
    else:
        pg.mixer.music.unpause()


def new_asterroid():
    Asterroid().add(all_sprites, mobs)


# Classes:


class Player(pg.sprite.Sprite):
    '''The spaceship sprite'''
    ship_imgs = {
        'x': (0, 32, 67, 99),
        'y': 192,
        'width': (32, 32, 30, 30),
        'height': 50
    }
    SOUNDS = glob(join(SOUNDS_FOLDER, 'sound_tracks', '**'))
    guns = glob(join(IMAGES_FOLDER, 'guns', '*png'))

    def __init__(self):
        super(Player, self).__init__()
        self.frame = 0
        self.missile = Ss(self.guns[1])
        self.image = shipsheet.get_image(BLACK, [
            self.ship_imgs['x'][self.frame], self.ship_imgs['y'],
            self.ship_imgs['width'][self.frame], self.ship_imgs['height']
        ], (40, 63))
        self.rect = self.image.get_rect()
        self.rect.bottom = HEIGHT - 10
        self.rect.centerx = WIDTH / 2
        self.radius = 10
        self.shield = 100
        self.lives = 3
        self.pwr_level = 1
        self.weapon = 1
        self.bombs = 1
        self.hidden = False
        self.flip = False
        self.hold_fire = True
        self.shoot_time = gtk()
        self.missile_time = self.shoot_time
        self.pwr_time = self.shoot_time
        self.strive = self.shoot_time
        self.hide_time = self.shoot_time

    def update(self):
        if self.hidden and gtk() - self.hide_time > 1500:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10
        key_state = pg.key.get_pressed()
        if (key_state[pg.K_LEFT]
                or key_state[pg.K_RIGHT]) and (key_state[pg.K_x]
                                               or key_state[pg.K_DOWN]):
            step = dt / 1.414
        else:
            step = dt
        if key_state[pg.K_LEFT]:
            self.rect.x -= step
            self.flip = False
        if key_state[pg.K_RIGHT]:
            self.rect.x += step
            self.flip = True
        if key_state[pg.K_RIGHT] or key_state[pg.K_LEFT]:
            if gtk() - self.strive > 100:
                self.strive = gtk()
                self.frame += 1
                if self.frame == 4:
                    self.frame = 3
        else:
            self.frame = 0
        if key_state[pg.K_x]:
            self.rect.y -= step
        if key_state[pg.K_DOWN]:
            self.rect.y += step
        if key_state[pg.K_SPACE] or self.hold_fire:
            self.shoot()
        if self.rect.right >= WIDTH:
            self.rect.right = WIDTH
        if self.rect.left <= 0:
            self.rect.left = 0
        if HEIGHT + 100 > self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT
        if self.rect.top <= 0:
            self.rect.top = 0
        self.image = shipsheet.get_image(BLACK, [
            self.ship_imgs['x'][self.frame], self.ship_imgs['y'],
            self.ship_imgs['width'][self.frame], self.ship_imgs['height']
        ], (40, 63), self.flip)

    def hide(self):
        self.hidden = True
        self.hide_time = gtk()
        self.rect.center = (2 * WIDTH, 2 * HEIGHT)

    def launch_missile(self):
        Missile(
            self.missile.get_image(BLACK),
            (self.rect.left, self.rect.centery)).add(all_sprites, bullets)
        Missile(
            self.missile.get_image(BLACK),
            (self.rect.right, self.rect.centery)).add(all_sprites, bullets)
        Missile(
            self.missile.get_image(BLACK),
            (self.rect.centerx, self.rect.top)).add(all_sprites, bullets)

    def shoot(self):
        now = gtk()
        if not self.hidden:
            if now - self.shoot_time > 250:
                self.shoot_time = now
                if self.weapon == 1:
                    pg.mixer.Sound(self.SOUNDS[2]).play()
                    Bullet(self.rect.centerx, self.rect.top).add(
                        all_sprites, bullets)
                elif self.weapon == 2:
                    pg.mixer.Sound(self.SOUNDS[3]).play()
                    Bullet(self.rect.left, self.rect.centery).add(
                        all_sprites, bullets)
                    Bullet(self.rect.right, self.rect.centery).add(
                        all_sprites, bullets)
                elif self.weapon == 3:
                    pg.mixer.Sound(self.SOUNDS[2]).play()
                    pg.mixer.Sound(self.SOUNDS[3]).play()
                    Bullet(self.rect.left, self.rect.centery, -1, 30).add(
                        all_sprites, bullets)
                    Bullet(self.rect.right, self.rect.centery, 1, -30).add(
                        all_sprites, bullets)
                    Bullet(self.rect.centerx, self.rect.top).add(
                        all_sprites, bullets)
                elif self.weapon == 5:
                    pg.mixer.Sound(self.SOUNDS[2]).play()
                    pg.mixer.Sound(self.SOUNDS[3]).play()
                    Bullet(self.rect.left, self.rect.centery).add(
                        all_sprites, bullets)
                    Bullet(self.rect.right, self.rect.centery).add(
                        all_sprites, bullets)
                    Bullet(self.rect.centerx, self.rect.top).add(
                        all_sprites, bullets)
                elif self.weapon == 6:
                    pg.mixer.Sound(self.SOUNDS[2]).play()
                    pg.mixer.Sound(self.SOUNDS[3]).play()
                    Bullet(self.rect.left, self.rect.centery).add(
                        all_sprites, bullets)
                    Bullet(self.rect.right, self.rect.centery).add(
                        all_sprites, bullets)
                    Bullet(self.rect.centerx, self.rect.top).add(
                        all_sprites, bullets)
                    Bullet(self.rect.left, self.rect.centery, -1.2, 35).add(
                        all_sprites, bullets)
                    Bullet(self.rect.right, self.rect.centery, 1.2, -35).add(
                        all_sprites, bullets)
                elif self.weapon == 7:
                    pg.mixer.Sound(self.SOUNDS[2]).play()
                    pg.mixer.Sound(self.SOUNDS[3]).play()
                    self.launch_missile()
                    Bullet(self.rect.left, self.rect.centery, -0.6, 16).add(
                        all_sprites, bullets)
                    Bullet(self.rect.right, self.rect.centery, 0.6, -16).add(
                        all_sprites, bullets)
                    Bullet(self.rect.centerx, self.rect.top).add(
                        all_sprites, bullets)
                    Bullet(self.rect.left, self.rect.centery, -1.2, 35).add(
                        all_sprites, bullets)
                    Bullet(self.rect.right, self.rect.centery, 1.2, -35).add(
                        all_sprites, bullets)
            if now - self.missile_time > 300 and self.weapon == 6:
                self.missile_time = now
                self.launch_missile()
            elif now - self.missile_time > 400 and self.weapon == 5:
                self.missile_time = now
                self.launch_missile()
            elif now - self.missile_time > 500 and self.weapon == 4:
                self.missile_time = now
                pg.mixer.Sound(self.SOUNDS[2]).play()
                pg.mixer.Sound(self.SOUNDS[3]).play()
                self.launch_missile()


    def bomb(self):
        global score
        pg.mixer.Sound(self.SOUNDS[8]).play()
        for mob in mobs:
            mob.shield -= 50
            if mob.shield < 0:
                mob.kill()
                mx = max(mob.rect.width, mob.rect.height)
                expl = Explosion(mob.rect.center, (mx, mx))
                all_sprites.add(expl)
                if type(mob) is not Asterroid:
                    score += 100 - mob.radius

    def shield_bar(self):
        if self.shield < 20:
            clr = RED
        else:
            clr = (36, 218, 181)
        pg.draw.rect(SCREEN, clr, [0, 0, self.shield, 20])
        pg.draw.rect(SCREEN, WHITE, [0, 0, 100, 20], 2)
        if self.shield > 0:
            text(SCREEN, '{}%'.format(self.shield), (50, 10), aconcepto16,
                 RED)


class Star(pg.sprite.Sprite):
    '''The stars in the background'''

    def __init__(self):
        super(Star, self).__init__()
        self.rand = randint(4, 7)
        self.image = pg.Surface((self.rand, self.rand))
        self.rect = self.image.get_rect()
        pg.draw.circle(self.image, WHITE, self.rect.center, self.rand // 2)
        self.image.set_colorkey(BLACK)
        self.rect.center = (randrange(WIDTH), randrange(-150, HEIGHT))

    def update(self):
        if self.rand < 6:
            self.rect.y += 0.2 * dt
        else:
            self.rect.y += 0.25 * dt
        if self.rect.top > HEIGHT:
            self.rect.center = (randrange(WIDTH), randrange(-150, 0))


class Bullet(pg.sprite.Sprite):
    '''The player's lazer bullets'''
    guns = glob(join(IMAGES_FOLDER, 'guns', '*png'))

    def __init__(self, x, y, direction=0, rot=0):
        super(Bullet, self).__init__()
        self.direction = direction
        self.rot = rot
        self.image = Ss(self.guns[0]).get_image(BLACK, angle=self.rot)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y

    def update(self):
        self.rect.y -= 2 * dt
        self.rect.x += self.direction * dt
        if self.rect.bottom < 0:
            self.kill()


class Missile(pg.sprite.Sprite):
    '''The player's guided missiles'''
    vect = pg.math.Vector2

    def __init__(self, image, center):
        super(Missile, self).__init__()
        self.max_speed = 18
        self.center = center
        self.image = image
        self.image_copy = self.image.copy()
        self.rect = self.image.get_rect()
        self.target = choice(mobs.sprites())
        self.pos = self.vect(self.center)
        self.vel = self.vect(0, -self.max_speed / 2)
        self.acc = self.vect(0, 0)
        self.rect.center = self.pos
        self.radius = 15
        self.shield = 5

    def seek(self, target):
        self.desired = (target - self.pos).normalize() * self.max_speed
        self.steer = (self.desired - self.vel)
        if self.steer.length() > 1:
            self.steer.scale_to_length(1)
        return self.steer

    def update(self):
        self.acc = self.seek(self.target.rect.center)
        if not self.target.alive() or type(self.target) is Asterroid:
            self.target = choice(mobs.sprites())
        self.vel += self.acc
        self.normal = self.vect(0, self.rect.centery)
        self.image = pg.transform.rotate(self.image_copy,
                                         self.vel.angle_to(self.normal) + 180)
        if self.vel.length() > self.max_speed:
            self.vel.scale_to_length(self.max_speed)
        self.pos += self.vel
        if self.pos.x < 0 or self.pos.x > WIDTH or self.pos.y > HEIGHT or self.pos.y < 0:
            self.kill()
        self.rect.center = self.pos


class MobMissile(pg.sprite.Sprite):
    '''The mob's guided missiles'''
    mobsheet2 = Ss(join(IMAGES_FOLDER, 'mobsheet2.png'))
    mob_missile_imgs = {
        'x': (0, 16, 32, 48),
        'y': 0,
        'width': 16,
        'height': 40
    }
    mob_missile_imgs2 = {
        'x': (0, 32, 64, 128),
        'y': 640,
        'width': 32,
        'height': 32
    }
    vect = pg.math.Vector2

    def __init__(self, center, bullet_type):
        super(MobMissile, self).__init__()
        self.type = bullet_type
        self.center = center
        self.frame = 0
        self.max_speed = 6
        if self.type == 'mmf':
            self.image = self.mobsheet2.get_image(BLACK, [
                self.mob_missile_imgs['x'][self.frame],
                self.mob_missile_imgs['y'], self.mob_missile_imgs['width'],
                self.mob_missile_imgs['height']
            ])
        else:
            self.image = self.mobsheet2.get_image(BLACK, [
                self.mob_missile_imgs2['x'][self.frame],
                self.mob_missile_imgs2['y'], self.mob_missile_imgs2['width'],
                self.mob_missile_imgs2['height']
            ], (16, 16))
        self.rect = self.image.get_rect()
        self.pos = self.vect(self.center)
        self.vel = (
            player.rect.center - self.pos).normalize() * 1.5 * self.max_speed
        self.acc = self.vect(0, 0)
        self.rect.center = self.pos
        self.radius = 5
        self.shield = 5
        self.next = gtk()

    def seek(self, target):
        self.desired = (target - self.pos).normalize() * self.max_speed
        self.steer = (self.desired - self.vel)
        if self.steer.length() > 0.4:
            self.steer.scale_to_length(0.4)
        return self.steer

    def update(self):
        if gtk() - self.next > 20:
            self.next = gtk()
            self.frame += 1
            if self.frame == len(self.mob_missile_imgs['x']):
                self.frame = 0
        if self.type == 'mmf':
            self.acc = self.seek(player.rect.center)
        else:
            self.acc = self.vect(0, 0)
        self.vel += self.acc
        if self.vel.length() > self.max_speed:
            self.vel.scale_to_length(self.max_speed)
        self.pos += self.vel
        if self.pos.x < 0 or self.pos.x > WIDTH or self.pos.y > HEIGHT or self.pos.y < 0:
            self.kill()
        if self.type == 'mmf':
            self.image = self.mobsheet2.get_image(BLACK, [
                self.mob_missile_imgs['x'][self.frame],
                self.mob_missile_imgs['y'], self.mob_missile_imgs['width'],
                self.mob_missile_imgs['height']
            ])
        else:
            self.image = self.mobsheet2.get_image(BLACK, [
                self.mob_missile_imgs2['x'][self.frame],
                self.mob_missile_imgs2['y'], self.mob_missile_imgs2['width'],
                self.mob_missile_imgs2['height']
            ], (16, 16))
        self.rect.center = self.pos


class Asterroid(pg.sprite.Sprite):
    '''The rocks floating in the space'''
    meteors = glob(join(IMAGES_FOLDER, 'meteors1', '*png'))

    def __init__(self):
        super(Asterroid, self).__init__()
        self.image = pg.image.load(choice(self.meteors)).convert()
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
        self.rot_time = gtk()

    def rotate(self):
        if gtk() - self.rot_time > 50:
            self.rot_time = gtk()
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
    explsheet = Ss(join(IMAGES_FOLDER, 'explsheet.png'))
    expl_imgs = {
        'x': tuple(int('{}00'.format(i)) for i in range(9)) * 8,
        'y': tuple(int('{}00'.format(i)) for i in range(8) for j in range(9)),
        'width': 100,
        'height': 100
    }

    def __init__(self, center, size):
        super(Explosion, self).__init__()
        self.size = size
        self.frame = 0
        self.image = self.explsheet.get_image(BLACK, [
            self.expl_imgs['x'][self.frame], self.expl_imgs['y'][self.frame],
            self.expl_imgs['width'], self.expl_imgs['height']
        ], self.size)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.time = gtk()

    def update(self):
        if gtk() - self.time > 1:
            self.time = gtk()
            self.frame += 6
            if self.frame == len(self.expl_imgs['x']):
                self.kill()
            else:
                center = self.rect.center
                self.image = self.explsheet.get_image(BLACK, [
                    self.expl_imgs['x'][self.frame],
                    self.expl_imgs['y'][self.frame], self.expl_imgs['width'],
                    self.expl_imgs['height']
                ], self.size)
                self.rect = self.image.get_rect()
                self.rect.center = center


class Powerup(pg.sprite.Sprite):
    '''All the POWERUPS: shield, weapon...'''
    POWERUPS = glob(join(IMAGES_FOLDER, 'powerups', '*png'))

    def __init__(self, center):
        super(Powerup, self).__init__()
        self.type = choice(self.POWERUPS)
        self.image = pg.image.load(self.type).convert()
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.center = center
        self.rect.center = center
        self.up = True

    def update(self):
        if self.rect.centery < self.center[1] - 50:
            self.up = False
        if self.up:
            self.rect.y -= dt / 2
        else:
            self.rect.y += dt / 4
        if self.rect.top > HEIGHT:
            self.kill()


class AlienShip(pg.sprite.Sprite):
    '''elongated grey alienship'''
    vect = pg.math.Vector2
    alien_ship = Ss(join(IMAGES_FOLDER, 'alienspaceship.png'))

    def __init__(self, x, y):
        super(AlienShip, self).__init__()
        self.max_speed = 10
        self.approach_radius = 100
        self.image = self.alien_ship.get_image(BLACK, size=(100, 100))
        self.x = x
        self.y = y
        self.xd = x
        self.yd = y + 200
        self.steer_force = 2
        self.rect = self.image.get_rect()
        self.pos = self.vect(self.x, self.y)
        self.vel = self.vect(0, self.max_speed)
        self.acc = self.vect(0, 0)
        self.radius = 50
        self.shield = 17
        self.right = True
        self.next = gtk()
        self.shoot_time = self.next
        self.dtime = self.next
        self.rect.center = self.pos

    def shoot(self):
        if gtk() - self.shoot_time > 3000:
            self.shoot_time = gtk()
            MobMissile(self.rect.center, 'mmdf').add(all_sprites, pwrups)

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
        now = gtk()
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


class AlienShip2(pg.sprite.Sprite):
    '''The elongted red alienship'''
    vect = pg.math.Vector2
    alien_ship2 = Ss(join(IMAGES_FOLDER, 'att2.png'))

    def __init__(self, x, y):
        super(AlienShip2, self).__init__()
        self.max_speed = 10
        self.approach_radius = 100
        self.image = self.alien_ship2.get_image(BLACK, size=(58, 100))
        self.x = x
        self.y = y
        self.xd = x
        self.yd = y + 200
        self.steer_force = 2
        self.rect = self.image.get_rect()
        self.pos = self.vect(self.x, self.y)
        self.vel = self.vect(0, self.max_speed)
        self.acc = self.vect(0, 0)
        self.radius = 40
        self.shield = 10
        self.right = True
        self.next = gtk()
        self.shoot_time = self.next
        self.dtime = self.next
        self.rect.center = self.pos
        self.c = 0
        self.then = self.next

    def shoot(self):
        if gtk() - self.shoot_time > 3000:
            self.shoot_time = gtk()
            MobMissile(self.rect.center, 'mmdf').add(all_sprites, pwrups)

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
        now = gtk()
        if now - self.then > 300:
            self.then = now
            self.c = (self.c + 5) % 360
            # self.Ss = (self.Ss + 1) % 360
        self.acc = self.vect(cos(self.c) * self.max_speed - 10, 10)
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


class Mob(pg.sprite.Sprite):
    '''The red eye-like alienship'''
    vect = pg.math.Vector2
    mobsheet = Ss(join(IMAGES_FOLDER, 'mobsheet.png'))
    mob_imgs = {
        'x': (0, 31, 63, 95, 127, 175, 223, 270),
        'y': 0,
        'width': (31, 32, 32, 32, 48, 48, 48, 48),
        'height': 80
    }

    def __init__(self, y):
        super(Mob, self).__init__()
        self.frame = 0
        self.y = y
        self.yd = self.y
        self.max_speed = 4
        self.steer_force = 0.2
        self.approach_radius = 100
        self.image = self.mobsheet.get_image(
            WHITE, (self.mob_imgs['x'][self.frame], self.mob_imgs['y'],
                    self.mob_imgs['width'][self.frame],
                    self.mob_imgs['height']))
        self.rect = self.image.get_rect()
        self.pos = self.vect(WIDTH + 40, self.y)
        self.vel = self.vect(-self.max_speed, 0)
        self.acc = self.vect(0, 0)
        self.xd = choice([-100, WIDTH + 100])
        self.radius = 50
        self.shield = 12
        self.next = gtk()
        self.shoot_time = self.next
        self.switch = False
        self.rect.center = self.pos

    def shoot(self):
        if gtk() - self.shoot_time > 4000:
            self.shoot_time = gtk()
            MobMissile(self.rect.center, 'mmdf').add(all_sprites, pwrups)

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
        if gtk() - self.next > 500:
            self.next = gtk()
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


class Mob2(pg.sprite.Sprite):
    '''The round alienship'''
    vect = pg.math.Vector2
    mobsheet2 = Ss(join(IMAGES_FOLDER, 'mobsheet2.png'))
    mob_imgs2 = {
        'x': (0, 95, 190, 285, 385, 480, 575),
        'y': (45, 270, 496, 718),
        'width': (95, 95, 95, 100, 95, 95, 95),
        'height': 90
    }

    def __init__(self):
        super(Mob2, self).__init__()
        self.frame = 0
        self.yd = randrange(WIDTH / 2)
        self.max_speed = 10
        self.steer_force = 0.2
        self.approach_radius = 100
        self.ch = choice(self.mob_imgs2['y'])
        self.image = self.mobsheet2.get_image(
            BLACK, (self.mob_imgs2['x'][self.frame], self.ch,
                    self.mob_imgs2['width'][self.frame],
                    self.mob_imgs2['height']))
        self.rect = self.image.get_rect()
        self.pos = self.vect(
            choice([randrange(-50, 0),
                    randrange(WIDTH, WIDTH + 50)]), self.yd)
        self.vel = self.vect(-self.max_speed, 0)
        self.acc = self.vect(0, 0)
        self.xd = self.pos.x
        self.radius = 50
        self.shield = 300
        self.next = gtk()
        self.shoot_time = self.next
        self.rect.center = self.pos
        self.switch = False

    def shoot(self):
        if gtk() - self.shoot_time > 2500:
            self.shoot_time = gtk()
            b_type = choice(['mmdf', 'mmf'])
            mm = MobMissile(self.rect.center, b_type)
            if b_type is 'mmf':
                mm.add(all_sprites, mobs)
            else:
                mm.add(all_sprites, pwrups)

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
        if gtk() - self.next > 500:
            self.next = gtk()
            self.frame += 1
            if self.frame == len(self.mob_imgs2['x']):
                self.frame = 0
        self.image = self.mobsheet2.get_image(
            BLACK, (self.mob_imgs2['x'][self.frame], self.ch,
                    self.mob_imgs2['width'][self.frame],
                    self.mob_imgs2['height']))
        if self.xd < 500:
            self.switch = False
        elif self.xd > 600:
            self.switch = True
        if self.switch:
            self.xd -= dt / 10
        else:
            self.xd += dt / 10
        if (self.vect(self.xd, self.yd) - self.pos).length():
            self.acc = self.seek_with_approach((self.xd, self.yd))
        self.vel += self.acc
        self.pos += self.vel
        self.rect.center = self.pos


# game_init:
all_sprites = pg.sprite.Group()
mobs = pg.sprite.Group()
stars = pg.sprite.Group()
pwrups = pg.sprite.Group()
bullets = pg.sprite.Group()
player = Player()
all_sprites.add(player)
mob2 = Mob2()
then = gtk()
ashs_time = then
ashs_time2 = then
mob_time = then
next_ash = then
next_ash2 = then
next_mob = then
next_mob2 = then
blink_time = then
wait_time = then
randy = randrange(40, HEIGHT // 3)
ashc = 0
ashc2 = 0
mobc = 0
msc = 0
score = 0
bring_ash = True
bring_ash2 = False
bring_mob2 = True
blink = False
wait = True
game_over = True
running = True
paused = False
hs = False
clock = pg.time.Clock()
# game loop:
while running:
    dt = clock.tick(FPS) // 2
    now = gtk()
    rand = random()
    music_player()
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_n:
                paused = True
            if event.key == pg.K_h:
                if player.hold_fire:
                    player.hold_fire = False
                else:
                    player.hold_fire = True
            if event.key == pg.K_w:
                player.weapon += 1
            if event.key == pg.K_b and player.bombs > 0:
                player.bomb()
                player.bombs -= 1
    while game_over:
        clock.tick(FPS)
        now = gtk()
        music_player()
        if len(stars) < 150:
            for i in range(150):
                Star().add(stars)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            if event.type == pg.KEYUP and not wait:
                game_over = False
        if now - wait_time > 1000:
            wait = False
        # initialisation:
        player.lives = 3
        player.bombs = 1
        player.pwr_level = 1
        player.weapon = 1
        player.rect.bottom = HEIGHT - 10
        player.rect.centerx = WIDTH / 2
        player.add(all_sprites)
        mobs.clear(SCREEN, SCREEN)
        SCREEN.fill(BLACK)
        stars.draw(SCREEN)
        text(SCREEN, "Shmup", (WIDTH / 2, HEIGHT / 4), aconcepto100,
             WHITE)
        text(SCREEN, 'Use Arrows To Move Space Bar To Shoot And B To Bomb',
             (WIDTH / 2, HEIGHT / 2), aconcepto16, WHITE)
        if now - blink_time > 1000:
            blink_time = now
            if blink:
                blink = False
            else:
                blink = True
        if blink:
            text(SCREEN, 'press any key', (WIDTH / 2, HEIGHT * 3 / 4),
                 aconcepto26, WHITE)
        stars.update()
        pg.display.flip()
    while paused:
        clock.tick(15)
        music_player()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_n:
                    paused = False
        text(SCREEN, 'paused', (WIDTH / 2, HEIGHT / 2), aconcepto100,
             WHITE)
        pg.display.flip()
    # collisions:
    hits = pg.sprite.groupcollide(mobs, bullets, False, True,
                                  pg.sprite.collide_circle)
    for hit in hits:
        if type(hit) is not Asterroid:
            score += int(100 - hit.radius)
        hit.shield -= 16
        if hit.shield < 0:
            hit.kill()
            mx = max(hit.rect.width, hit.rect.height)
            expl = Explosion(hit.rect.center, (mx, mx))
            all_sprites.add(expl)
            if 0.1 < rand < 0.4:
                new_asterroid()
            if type(hit) in {AlienShip, AlienShip2, Mob}:
                if rand > 0.9:
                    pwr = Powerup(hit.rect.center)
                    pwr.add(all_sprites, pwrups)
            elif type(hit) is Mob2:
                if rand > 0.8:
                    pwr = Powerup(hit.rect.center)
                    pwr.add(all_sprites, pwrups)
            elif rand > 0.99:
                pwr = Powerup(hit.rect.center)
                pwr.add(all_sprites, pwrups)
        else:
            mx = max(hit.rect.width // 2, hit.rect.height // 2)
            expl = Explosion(hit.rect.center, (mx, mx))
            all_sprites.add(expl)
    beats = pg.sprite.spritecollide(player, mobs, True,
                                    pg.sprite.collide_circle)
    for beat in beats:
        get_hit(beat)
    power = pg.sprite.spritecollide(player, pwrups, True, pg.sprite.collide_circle)
    for pwr in power:
        if pwr.type == POWERUPS[0]:
            pg.mixer.Sound(SOUNDS[6]).play()
            player.pwr_level += 1
            if player.pwr_level <= 7:
                player.weapon += 1
            player.pwr_time = gtk()
        if pwr.type == POWERUPS[1]:
            player.shield += randrange(10, 30)
            player.pwr_time = gtk()
            if player.shield >= 100:
                player.shield = 100
        if pwr.type == POWERUPS[2]:
            player.bombs += 1
            if player.bombs < 0:
                player.bombs = 0
            if player.bombs > 3:
                player.bombs = 3
        if pwr.type == 'mmdf':
            get_hit(pwr)
    if player.pwr_level < 1:
        player.pwr_level = 1
    if player.pwr_level > 7:
        player.pwr_level = 7
    if player.weapon > player.pwr_level:
        player.weapon = 1
    if now - player.pwr_time > 60000:
        player.pwr_time = now
        player.pwr_level -= 1
        pg.mixer.Sound(SOUNDS[4]).play()
    # draw:
    SCREEN.fill(BLACK)
    if now - ashs_time > 10000:
        ashs_time = now
        bring_ash = True
    if now - next_ash > 500 and bring_ash:
        next_ash = now
        ashc += 1
        AlienShip(200, -50).add(all_sprites, mobs)
        if ashc > 5:
            ashc = 0
            bring_ash = False
    if now - ashs_time2 > 8000:
        ashs_time2 = now
        bring_ash2 = True
    if now - next_ash2 > 200 and bring_ash2:
        ashc2 += 1
        next_ash2 = now
        AlienShip2(500, -200).add(all_sprites, mobs)
        if ashc2 > 5:
            ashc2 = 0
            bring_ash2 = False
    if now - next_mob2 > 6000:
        next_mob2 = now
        if rand > .6:
            Mob2().add(all_sprites, mobs)
    if now - next_mob > 12000:
        next_mob = now
        if rand < .9:
            mobc = 0
            randy = randrange(40, HEIGHT // 3)
    if now - mob_time > 500 and mobc < 12:
        mob_time = now
        mobc += 1
        Mob(randy).add(all_sprites, mobs)
    for i in range(player.lives):
        SCREEN.blit(mini_ship, ((WIDTH - 90) + 30 * i, 10))
    for i in range(player.bombs):
        SCREEN.blit(mini_bomb, (110 + 30 * i, 5))
    if len(mobs) < 5:
        for i in range(7):
            new_asterroid()
    stars.draw(SCREEN)
    all_sprites.draw(SCREEN)
    text(SCREEN, 'Score:{}'.format(score), (WIDTH / 2, 10), aconcepto20,
         WHITE)
    text(SCREEN, 'weapon:{}/{}'.format(player.weapon, player.pwr_level),
         (WIDTH * 3 / 4, 10), aconcepto16, RED)
    player.shield_bar()
    # update:
    stars.update()
    all_sprites.update()
    pg.display.flip()
pg.quit()
