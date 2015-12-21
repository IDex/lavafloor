# impossible pökö
import random
import pygame as pg
import pygame.locals as pgl
import pdb

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
SCREEN_RES = {'x': 600, 'y': 500}
FPS = 60
VY_JUMP = 25
VX = 10
VY = 1


class Projectile(pg.sprite.Sprite):
    """Models a flying projectile in the game"""

    def __init__(self, x, y):
        super().__init__()
        self.vel = (5, 0)
        self.rect = pg.Rect(x, y, 40, 10)

    def update(self, game):
        """Move the projectile while it's on the screen"""
        self.rect.move_ip(self.vel[0], self.vel[1])
        if self.rect.left > SCREEN_RES['x']:
            game.score += 1
            self.kill()
        pg.draw.rect(game.screen, BLACK, self.rect)

    @classmethod
    def make_projectiles(cls, rate):
        """Make a projectile every n:th call"""
        n = 1
        while True:
            if not n % rate:
                yield cls(0, random.randint(
                    int(SCREEN_RES['y']*2/3), SCREEN_RES['y'] - 10))
            n += 1
            yield


class Lava(pg.sprite.Sprite):
    """Models lava floor"""

    def __init__(self):
        super().__init__()
        self.vx = 5
        self.rect = pg.Rect(
            0, SCREEN_RES['y'] - 10, SCREEN_RES['x'] * 3 / 2, 10)
        self.rect.right = -SCREEN_RES['x']

    def update(self, game):
        """Move on the floor until the whole floor is covered in lava"""
        if self.rect.right > SCREEN_RES['x']:
            pass
        else:
            self.rect.move_ip(self.vx, 0)
        pg.draw.rect(game.screen, RED, self.rect)


class Player(pg.sprite.Sprite):
    """Models the player character"""

    def __init__(self):
        super().__init__()
        self.rect = pg.Rect(50, 50, 50, 50)
        self.can_jump = False
        self.vspeed = 0
        self.score = 0
        self.move = {pgl.K_RIGHT: (VX, 0),
                     pgl.K_LEFT: (-VX, 0)}

    def jump(self):
        """Accelerate player upwards"""
        self.vspeed -= VY_JUMP
        self.can_jump = False

    def update(self, game):
        """Update player's state and check for lava collision"""
        screen = game.screen
        self.vspeed += VY
        self.rect.move_ip(0, self.vspeed)
        if self.rect.top < 0:
            self.rect.top = 0
            self.vspeed = 0
        if self.rect.bottom > SCREEN_RES['y']:
            self.rect.bottom = SCREEN_RES['y']
            self.vspeed = 0
            self.can_jump = True
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_RES['x']:
            self.rect.right = SCREEN_RES['x']
        for obj in game.objects:
            if self.rect.colliderect(obj.rect) and obj != self:
                if self.vspeed > 0 and\
                self.rect.bottom - obj.rect.top < 30 and\
                not isinstance(obj, Lava):
                    self.rect.bottom = obj.rect.top
                    self.can_jump = True
                    self.vspeed = 0
        for obj in game.objects:
            if self.rect.colliderect(obj.rect) and obj != self:
                if isinstance(obj, Lava):
                    game.printscreen('Game Over, final score: '.split() +
                                     [str(game.score)], 3)
                    game.running = False
                    return
        pg.draw.rect(screen, BLACK, self.rect)


class Game:
    """Master class that manages game state and game/event loop"""

    def __init__(self, help=True):
        pg.display.set_caption('Impossible Pökö')
        self.screen = pg.display.set_mode(
            (SCREEN_RES['x'], SCREEN_RES['y']))
        self.font = pg.font.SysFont(None, 32, bold=True)
        self.bg_text = self.font.render(
            'Impossible Pökö ', True, BLACK)
        self.objects = pg.sprite.Group()
        self.player = Player()
        self.lava = Lava()
        self.objects.add(self.player)
        self.objects.add(self.lava)
        self.score = 0
        self.running = True
        self.help = help

    def printscreen(self, msg, delay):
        """Print a message on the screen for delay seconds"""
        self.screen.fill(WHITE)
        font = pg.font.SysFont(None, 32, bold=True)
        text = font.render(' '.join(msg), True, BLACK)
        self.screen.blit(
            text, (SCREEN_RES['x'] / len(msg), SCREEN_RES['y'] / 2))
        pg.display.update()
        pg.time.wait(int(delay * 1000))

    def check_events(self):
        """Check for new events and respond appropriately"""
        for event in pg.event.get():
            if event.type == pgl.KEYDOWN:
                if event.key == pgl.K_ESCAPE:
                    raise SystemExit
                elif event.key == pgl.K_UP and self.player.can_jump:
                    self.player.jump()
        for key in self.player.move.keys():
            if pg.key.get_pressed()[key]:
                self.player.rect.move_ip(self.player.move[key][0],
                                         self.player.move[key][1])

    def run(self):
        """Run the game loop"""
        clock = pg.time.Clock()
        # make a generator for projectiles
        make_proj = Projectile.make_projectiles(FPS / 2)
        if self.help:
            self.printscreen('Move with arrow keys'.split(), 1)
            self.printscreen('Jump on black blocks'.split(), 1)
            self.printscreen('Avoid lava floor'.split(), 1)
        else:
            self.printscreen('Practice makes perfect'.split(), 1)
        while self.running:
            try:
                make_proj.__next__().add(self.objects)
            except AttributeError:
                pass
            clock.tick(FPS)
            self.check_events()
            self.bg_text = self.font.render(
                'Impossible Pökö ' + str(self.score), True, BLACK)
            self.screen.fill(WHITE)
            self.screen.blit(
                self.bg_text, (SCREEN_RES['x'] / 2, SCREEN_RES['y'] / 2))
            self.objects.update(self)
            pg.display.update()
        


pg.init()
Game().run()
while True:
    Game(help=False).run()
