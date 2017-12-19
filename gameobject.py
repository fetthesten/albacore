import pygame.sprite as sprite
from pygame.math import Vector2 as Vector2


class ObjectManager:
    def __init__(self, prototypes):
        self.prototypes = prototypes
        self.objects = []

        # sprite groups
        self.sprites_all = sprite.Group()
        self.sprites_draw = sprite.Group()
        self.sprites_updateonly = sprite.Group()

        # movement mode controls... how things move
        # strings because that's great
        # possible values:
        # platform
        # topdown
        # more in the future!!!
        self.movement_mode = 'platform'
        self.gravity = Vector2(0.0, 0.1)

    def add(self, obj):
        # if obj in self.prototypes.keys():
        #    pass
        self.objects.append(PlayerControlledSprite(obj, 100, 100))
        self.objects[-1].add(self.sprites_all, self.sprites_draw)

    def update(self, input_data):
        self.sprites_all.update(input_data)

    def draw(self, surf):
        self.sprites_draw.draw(surf)

class MovingSprite(sprite.Sprite):
    def __init__(self, spr, x, y, movement_mode=False, gravity=False):
        sprite.Sprite.__init__(self)

        self.image = spr

        self.rect = self.image.get_rect()
        self.rect.center = x, y

        self.speed = 1
        self.accel = 1
        self.decel = 1

        self.direction = Vector2(0, 0)
        self.move = Vector2(0, 0)
        self.deadzone = 0.5

        # todo: make this suck less
        self.movement_mode = movement_mode
        if self.movement_mode is False:
            self.movement_mode = 'topdown'
        self.gravity = gravity
        if self.gravity is False:
            self.gravity = Vector2(0.0, 0.1)

    def update(self):
        self.movement()
        self.collision()
        self.rect.center += self.move
        sprite.Sprite.update(self)

    def movement(self):
        if self.direction.length() > 0:
            if self.movement_mode is 'topdown':
                self.move += self.direction
                self.move.x = -self.move.x if self.move.x < 0 else self.move.x
                self.move.y = -self.move.y if self.move.y < 0 else self.move.y
                self.move.x = self.move.x if self.move.x < self.speed else self.speed
                self.move.y = self.move.y if self.move.y < self.speed else self.speed
                #self.move.angle = self.direction.angle
            elif self.movement_mode is 'platform':
                self.move.x += self.direction.x
                self.move.x = -self.move.x if self.move.x < 0 else self.move.x
                self.move.x = self.move.x if self.move.x < self.speed else self.speed
                self.move.x *= self.direction.x
        else:
            if self.movement_mode is 'topdown':
                b = self.move
                self.move.x = -self.move.x if self.move.x < 0 else self.move.x
                self.move.y = -self.move.y if self.move.y < 0 else self.move.y
                self.move.x = self.move.x - self.decel if self.move.x > 0 else 0
                self.move.y = self.move.y - self.decel if self.move.y > 0 else 0
                self.move.x = 0 if self.move.x < 0 else self.move.x
                self.move.x = 0 if self.move.y < 0 else self.move.y
                self.move.x = -self.move.x if b.x < 0 else self.move.x
                self.move.y = -self.move.y if b.y < 0 else self.move.y
            elif self.movement_mode is 'platform':
                b = self.move
                self.move.x = -self.move.x if self.move.x < 0 else self.move.x
                self.move.x = self.move.x - self.decel if self.move.x > 0 else 0
                self.move.x = -self.move.x if b.x < 0 else self.move.x

        if self.movement_mode is 'platform':
            self.move += self.gravity

    def collision(self):
        pass


class PlayerControlledSprite(MovingSprite):
    def __init__(self, spr, x, y, movement_mode=False, gravity=False):
        MovingSprite.__init__(self, spr, x, y, movement_mode, gravity)

    def update(self, input_data):
        self.direction[0] = input_data['axes']['player1_move_horiz']['value']
        self.direction[1] = input_data['axes']['player1_move_vert']['value']
        MovingSprite.update(self)
