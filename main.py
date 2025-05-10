# Example file showing a basic pygame "game loop"
import pygame
import win32con
import win32gui
import win32api
import random
import pyautogui
import os
from pathlib import Path
import sys

def resource_path(relative_path):
    """Get the absolute path to the resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # If we are still in dev mode, make our paths start from the folder this file is in
        base_path = Path(__file__).parent

    return os.path.join(base_path, relative_path)

# states to the # of animation pics
STATE_ANIMS = {"SLEEP": 4 - 1, "IDLE": 6 - 1, "RUN": 6 - 1, "SCRATCH": 4 - 1, "CRY": 4 - 1}
STATE_PROBABILITIES = {"SLEEP": 50, "IDLE": 33, "RUN": 45}

STATES = list(STATE_PROBABILITIES.keys())
WEIGHTS = list(STATE_PROBABILITIES.values())

# cat width and height
SCREENWIDTH = win32api.GetSystemMetrics(0)
SCREENHEIGHT = win32api.GetSystemMetrics(1)

WIDTH = 128
HEIGHT = 128

# keep hitbox on mouse
class Mouse(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.sprite = pygame.Surface([1, 1])
        mousepos = pyautogui.position()
        self.rect = pygame.Rect(mousepos.x - cat.x ,mousepos.y - cat.y,1,1)
        mask = pygame.mask.from_surface(self.sprite)
        self.hitbox = mask

    def update(self):
        mousepos = pyautogui.position()
        mask = pygame.mask.from_surface(self.sprite)
        self.rect.center = mousepos.x - cat.x ,mousepos.y - cat.y
        self.hitbox = mask

class Cat(pygame.sprite.Sprite):
    def __init__(self, width, height):
        super().__init__()
        self.x = SCREENWIDTH // 2
        self.y = SCREENHEIGHT - HEIGHT
        self.normal_cat_height = SCREENHEIGHT - HEIGHT
        self.run_cat_height = (SCREENHEIGHT - HEIGHT) + 10
        self.state = "IDLE"
        self.facing = "LEFT"
        self.statecounter = 0
        self.last_state_change = -10000
        self.touched_last = -10
        self.last_touched = False
        # in milliseconds
        self.state_change_cooldown = 10000
        # this keeps track of switching sprite animations
        self.lastupdated = -10000
        self.width = width
        self.height = height
        self.sheet = pygame.image.load(resource_path('assets/catblue.png')).convert_alpha()

        self.image = self.get_sprite(0, 0)
        self.rect = self.image.get_rect()
        mask = pygame.mask.from_surface(self.image)
        self.hitbox = mask
        
    def get_sprite(self, x, y):
        sprite = pygame.Surface([64, 64])
        sprite.blit(self.sheet, (0,0), (x, y, 64, 64))
        sprite.set_colorkey((0,0,255))
        sprite = pygame.transform.scale(sprite, (WIDTH, HEIGHT))
        return sprite
    
    def update(self):
        # get current tick
        curr_tick = pygame.time.get_ticks()

        # update hitbox
        mask = pygame.mask.from_surface(self.image)
        self.hitbox = mask

        # if mouse touching cat, get scratches! 15
        offset = (mouse.rect.left - cat.rect.left, mouse.rect.top - cat.rect.top)
        if self.hitbox.overlap(mouse.hitbox, offset):
            self.touched_last = curr_tick
            self.last_touched = True
        
        # touched last
        if curr_tick - self.touched_last < 1000 and self.last_touched:
            self.state = "SCRATCH"
            if curr_tick - self.lastupdated > 300:
                self.lastupdated = curr_tick
                # update state for image
                self.statecounter += 1
                if self.statecounter >= STATE_ANIMS[self.state]:
                    self.statecounter = 0
                
                # update image
                sprite = self.get_sprite(64 * self.statecounter, 64 * 14)
                if self.facing == "RIGHT":
                    sprite = pygame.transform.flip(sprite, True, False)
                self.image = sprite
            self.rect = self.image.get_rect()
            self.last_state_change = -5
        
        # more than 10 min without touching
        elif curr_tick - self.touched_last > 10 * 60 * 1000:
            if curr_tick - self.lastupdated > 250:
                self.lastupdated = curr_tick
                self.state = "CRY"
                # update state for image
                self.statecounter += 1
                if self.statecounter >= STATE_ANIMS[self.state]:
                    self.statecounter = 0
                
                # update image
                sprite = self.get_sprite(64 * self.statecounter, 64 * 10)
                if self.facing == "RIGHT":
                    sprite = pygame.transform.flip(sprite, True, False)
                self.image = sprite
                self.rect = self.image.get_rect()
        
        # changing state randomly!
        elif curr_tick - self.last_state_change > self.state_change_cooldown:
            # if cat was being pet, now go into idle instead of random state
            if self.last_touched:
                self.state = "IDLE"
                self.last_touched = False
                self.last_state_change = curr_tick
            else:
                newstate = random.choices(STATES, weights=WEIGHTS, k=1)[0]
                if newstate != self.state:
                    self.state = newstate
                    self.statecounter = 0
                    self.lastupdated = -5
                    self.last_state_change = curr_tick

        # update the cat height because we change it when cat is running since our sprite sheet is weird
        self.y = self.normal_cat_height

        # only update sleep every 1000 ticks
        if self.state == "SLEEP":
            if curr_tick - self.lastupdated > 1000:
                self.lastupdated = curr_tick
                # update state for image
                self.statecounter += 1
                if self.statecounter >= STATE_ANIMS[self.state]:
                    self.statecounter = 0
                
                # update image
                sprite = self.get_sprite(64 * self.statecounter, 64 * 3)
                if self.facing == "RIGHT":
                    sprite = pygame.transform.flip(sprite, True, False)
                self.image = sprite
                self.rect = self.image.get_rect()
        
        # only update idle every 400 ticks
        elif self.state == "IDLE":
            if curr_tick - self.lastupdated > 400:
                self.lastupdated = curr_tick
                # update state for image
                self.statecounter += 1
                if self.statecounter >= STATE_ANIMS[self.state]:
                    self.statecounter = 0
                
                # update image
                sprite = self.get_sprite(64 * self.statecounter, 64 * 0)
                if self.facing == "RIGHT":
                    sprite = pygame.transform.flip(sprite, True, False)
                self.image = sprite
                self.rect = self.image.get_rect()

        elif self.state == "RUN":
            self.y = self.run_cat_height
            if curr_tick - self.lastupdated > 100:
                self.lastupdated = curr_tick
                # update state for image
                self.statecounter += 1
                if self.statecounter >= STATE_ANIMS[self.state]:
                    self.statecounter = 0
                
                # update image
                sprite = self.get_sprite(64 * self.statecounter, 64 * 5)
                if self.facing == "LEFT":
                    sprite = pygame.transform.flip(sprite, True, False)
                self.image = sprite
                self.rect = self.image.get_rect()
            
            if self.facing == "LEFT":
                self.x -= 3
                if self.x < 0:
                    self.facing = "RIGHT"
            else:
                self.x += 3
                if self.x > SCREENWIDTH - WIDTH:
                    self.facing = "LEFT"

# pygame setup
pygame.init()
pygame.display.set_caption('Pepper!')
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
clock = pygame.time.Clock()
running = True


cat = Cat(WIDTH, HEIGHT)
mouse = Mouse()
cat_group = pygame.sprite.Group(cat)

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


    # fill the screen with a color to wipe away anything from last frame
    screen.fill((255,255,0))

    # RENDER YOUR GAME HERE
    mouse.update()
    cat.update()
    cat_group.draw(screen)

    # make window transparent
    hwnd = pygame.display.get_wm_info()["window"]
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE ) | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
    win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(255,255,0), 0, win32con.LWA_COLORKEY)

    # place it at desired screen position and topmost
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST,
                      cat.x, cat.y, WIDTH, HEIGHT,
                      win32con.SWP_SHOWWINDOW)
    
    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(30)  # limits FPS to 30

pygame.quit()