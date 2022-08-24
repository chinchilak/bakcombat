import pygame
from pygame.locals import *
import random, math
import os


SWIDTH  = 1920
SHEIGHT = 1080
IMGSCALE = 4

pygame.init()

clock = pygame.time.Clock()
fps = 60
bottom_panel = 300
img_height = 100
img_width = 40

col = 200
row = 40
padding = 20

current_fighter = 1
total_fighters = 3
action_cooldown = 0
action_wait_time = 50
attack = False
clicked = False
game_over = 0

screen = pygame.display.set_mode((SWIDTH, SHEIGHT))
pygame.display.set_caption("Combat")

font = pygame.font.Font(("./assets/bak_std.ttf"),56)
font2 = pygame.font.Font(("./assets/bak_std.ttf"),96)

red = (255, 0, 0)
green = (0, 255, 0)
white = (255, 255, 255)

background_img = pygame.transform.scale(pygame.image.load("./graphics/Combat/background.png").convert_alpha(), (SWIDTH, SHEIGHT))
panel_img = pygame.transform.scale(pygame.image.load("./graphics/Combat/panel.png").convert_alpha(), (SWIDTH, SHEIGHT))
sword_img = pygame.image.load("./graphics/Combat/sword.png").convert_alpha()

def count_files_in_dir(dirpath:str):
    return (len([e for e in os.listdir(dirpath) if os.path.isfile(os.path.join(dirpath, e))]))

def get_chance_result(chance:float):
    if math.floor(random.uniform(0, 1/(1-chance))) == 1:
        return True
    else:
        return False

def draw_text(text, font, text_col, x, y):
    screen.blit(font.render(text, True, text_col), (x, y))

def draw_bg():
    screen.blit(background_img, (0, 0))


class Button():
	def __init__(self, surface, x, y, image, size_x, size_y):
		self.image = pygame.transform.scale(image, (size_x, size_y))
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False
		self.surface = surface

	def draw(self):
		action = False
		pos = pygame.mouse.get_pos()
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				action = True
				self.clicked = True
		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False
		#draw button
		self.surface.blit(self.image, (self.rect.x, self.rect.y))
		return action

stats = {
    "Gorath": {
        "health"   : 60,
        "stamina"  : 65,
        "speed"    : 3,
        "strength" : 25,
        "melee"    : 65,
        "defense"  : 43,
        "haggle"   : 9,
        "lockpick" : 15,
        "scout"    : 45},
    "Bandit": {
        "health"   : 40,
        "stamina"  : 20,
        "speed"    : 1,
        "strength" : 17,
        "melee"    : 42,
        "defense"  : 30}}

#player class
class Player():
    def __init__(self, x, y, name):
        self.name = name
        self.max_hp = stats[self.name]["health"] + stats[self.name]["stamina"]
        self.hp = self.max_hp
        self.strength = stats[self.name]["strength"]
        self.melee = stats[self.name]["melee"]
        self.defense = stats[self.name]["defense"]
        self.alive = True
        self.animation_list = []
        self.frame_index = 0
        self.action = 0 # 0:idle, 1:attack, 2:hurt, 3:dead
        self.update_time = pygame.time.get_ticks()
        dirname = "./graphics"
        dirlst = ["idle", "attack", "hurt", "death"]
        for dir in dirlst:
            pth = dirname + "/" + self.name + "/" + dir
            temp_list = []
            for i in range(count_files_in_dir(pth)):
                img = pygame.image.load(pth + "/" + str(i) + ".png")
                img = pygame.transform.scale(img, (img.get_width() * IMGSCALE, img.get_height() * IMGSCALE))
                temp_list.append(img)
            self.animation_list.append(temp_list)
        self.animation_list.append(temp_list)
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        animation_cooldown = 120
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        #if the animation has run out then reset back to the start
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.idle()

    def idle(self):
        self.action = 0
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def attack(self, target):
        weaponacc = 8
        weapondmg = 10
        defense = stats["Bandit"]["defense"]
        self.tohit = self.melee + weaponacc
        # rand = random.randint(-5, 5)
        getchance = get_chance_result(self.tohit/100)

        if getchance:
            damage = self.strength + weapondmg - defense//2
            target.hp -= damage
            target.hurt()
            damage_text = DamageText(target.rect.centerx, target.rect.y, "-" + str(damage), red)
            damage_text_group.add(damage_text)
        else:
            damage_text = DamageText(target.rect.centerx, target.rect.y, str("M i s s"), red)
            damage_text_group.add(damage_text)

        if target.hp < 1:
            target.hp = 0
            target.alive = False
            target.death()
        
        self.action = 1
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def hurt(self):
        self.action = 2
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def death(self):
        self.action = 3
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def draw(self):
        screen.blit(self.image, self.rect)

class HealthBar():
    def __init__(self, x, y, hp, max_hp):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = max_hp

    def draw(self, hp):
        self.hp = hp
        ratio = self.hp / self.max_hp
        pygame.draw.rect(screen, red, (self.x, self.y, 160, row))
        pygame.draw.rect(screen, green, (self.x, self.y, 160 * ratio, row))

class DamageText(pygame.sprite.Sprite):
    def __init__(self, x, y, damage, colour):
        pygame.sprite.Sprite.__init__(self)
        self.image = font.render(damage, True, colour)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        self.rect.y -= 1
        self.counter += 1
        if self.counter > 60:
            self.kill()

damage_text_group = pygame.sprite.Group()

knight = Player(padding + img_width * 2, SHEIGHT - bottom_panel - img_height, "Gorath")

bandit_list = []
for cnt in range(total_fighters - 1):
    bandit_list.append(Player(SWIDTH//2 + padding + img_width * 2 + cnt * col, SHEIGHT - bottom_panel - img_height + padding//2, "Bandit"))

def draw_panel():
    screen.blit(panel_img, (0, SHEIGHT - bottom_panel))

    draw_text(f"{knight.name}", font, red, padding*2, SHEIGHT - bottom_panel + padding)
    draw_text(f"HP: {knight.hp}", font, red, padding*2, SHEIGHT - bottom_panel + padding + row)
    HealthBar(padding*2, SHEIGHT - bottom_panel + padding + row * 2, knight.hp, knight.max_hp).draw(knight.hp)

    for cnt, val in enumerate(bandit_list):
        draw_text(f"{val.name}" + " " + str(cnt+1), font, red, SWIDTH//2 + padding*2 + (cnt * col), (SHEIGHT - bottom_panel + padding))
        draw_text(f"HP: {val.hp}", font, red, SWIDTH//2 + padding*2 + (cnt * col), (SHEIGHT - bottom_panel + padding + row))
        HealthBar(SWIDTH//2 + padding*2 + (cnt * col), (SHEIGHT - bottom_panel + padding + row * 2), val.hp, val.max_hp).draw(val.hp)


run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            clicked = True
    clock.tick(fps)

    draw_bg()
    draw_panel()

    pygame.draw.line(screen, (0,0,0), (SWIDTH//2, 0), (SWIDTH//2,SHEIGHT), 3)
    knight.update()
    knight.draw()
    for bandit in bandit_list:
        bandit.update()
        bandit.draw()
    damage_text_group.update()
    damage_text_group.draw(screen)
    attack = False
    target = None
    pygame.mouse.set_visible(True)
    pos = pygame.mouse.get_pos()
    for count, bandit in enumerate(bandit_list):
        if bandit.rect.collidepoint(pos):
            pygame.mouse.set_visible(False)
            screen.blit(sword_img, pos)
            if clicked == True and bandit.alive == True:
                attack = True
                target = bandit_list[count]
                clicked = False

    if game_over == 0:
        #player action
        if knight.alive == True:
            if current_fighter == 1:
                action_cooldown += 1
                if action_cooldown >= action_wait_time:
                    if attack == True and target != None:
                        knight.attack(target)
                        current_fighter += 1
                        action_cooldown = 0
        else:
            game_over = -1

        #enemy action
        for count, bandit in enumerate(bandit_list):
            if current_fighter == 2 + count:
                if bandit.alive == True:
                    action_cooldown += 1
                    if action_cooldown >= action_wait_time:
                        bandit.attack(knight)
                        current_fighter += 1
                        action_cooldown = 0
                else:
                    current_fighter += 1

        #if all fighters have had a turn then reset
        if current_fighter > total_fighters:
            current_fighter = 1

    #check if all bandits are dead
    alive_bandits = 0
    for bandit in bandit_list:
        if bandit.alive == True:
            alive_bandits += 1
    if alive_bandits == 0:
        game_over = 1

    #check if game is over
    if game_over != 0:
        if game_over == 1:
            txt = "V I C T O R Y"
            screen.blit(pygame.font.Font(("./assets/bak_std.ttf"),96).render(txt, True, red), (SWIDTH//2 - font2.size(txt)[0]//2, SHEIGHT//4))
        if game_over == -1:
            txt = "D E F E A T"
            screen.blit(pygame.font.Font(("./assets/bak_std.ttf"),96).render(txt, True, red), (SWIDTH//2 - font2.size(txt)[0]//2, SHEIGHT//4))

    pygame.display.update()

pygame.quit()