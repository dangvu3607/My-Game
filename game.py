# Importing modules
import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join
# Initiating pygame
pygame.init()
pygame.mixer.init()

# Stating variables for the platform:
WIDTH, HEIGHT = 800, 600
FPS = 60
PLAYER_VEL = 5
game_active = True


# Set caption and dimension of the platform:
pygame.display.set_caption("Platformer")
window = pygame.display.set_mode((WIDTH, HEIGHT))

# Flip the sprite direction on the x-axis when moving left or right
def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    # Specify the directorys (assets>dir1>dir2)
    path = join("assets", dir1, dir2)
    # Creat a list of sprites from the directory
    images = [f for f in listdir(path) if isfile(join(path, f))]

    # Dictionary contains key:value of the sprites (E.g: idle_right:sprites)
    all_sprites = {}

    # Delete background of sprites, add it to sprites list and define direction if required
    for image in images:
        # Delete background of sprites sheets
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        # Create a sprites list
        sprites = []

        for i in range(sprite_sheet.get_width() // width):
            
            # Make a surface source
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)

            # State the area to draw
            rect = pygame.Rect(i * width, 0, width, height)

            # Draw the intended source, onto coordinate, in an area then double the size
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        # Stating key:value for directional sprites
        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites


def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)

    return pygame.transform.scale2x(surface)
'''
class Button():
    def __init__(self, x, y, name) -> None:
        self.image = pygame.image.load(join("assets", "Button", name))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


    def draw(self, window):
        window.blit(self.image, (self.rect.x, self.rect.y))
'''
class Player(pygame.sprite.Sprite):

    # Player is a pointer-rectangle
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "HoodedGuy", 32, 32, True)
    ANIMATION_DELAY = 3

    # Player's attributes
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x , y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        self.hit_point = 3
    
    def jump(self):
        self.y_vel = -self.GRAVITY * 10
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def make_hit(self):
        self.hit = True
        self.hit_count = 0
        

    # Player's movement method
    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    # Player's loop and gravity method
    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
            
            
        if self.hit_count > fps /5:
            self.hit = False
            self.hit_count = 0
            self.hit_point += -1
            if self.hit_point == 0:
                global game_active
                game_active = False
            

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        if self.hit_point == 0 or not game_active:
            sprite_sheet = "death"
        
        if game_active:
            sprite_sheet = "idle"
            if self.hit:
                sprite_sheet = "hit"
            elif self.y_vel < 0:
                if self.jump_count == 1:
                    sprite_sheet = "jump"
                elif self. jump_count == 2:
                    sprite_sheet = "double_jump"
            elif self.y_vel > self.GRAVITY * 2:
                sprite_sheet = "fall"
            elif self.x_vel != 0:
                sprite_sheet = "run"
        
        
        

        sprite_sheet_name = f"{sprite_sheet}_{self.direction}"
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // 
                        self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()
        
    def update(self):
        self.rect = self.sprite.get_rect(topleft = (self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, window, offset_x, offset_y):
        window.blit(self.sprite, (self.rect.x - offset_x, self.rect.y - offset_y))


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, window, offset_x, offset_y):
        window.blit(self.image,(self.rect.x - offset_x, self.rect.y - offset_y))


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0,0))
        self.mask = pygame.mask.from_surface(self.image)


class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x ,y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def move(self, dy):
        self.rect.y += dy

    def loop(self, vel):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft = (self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

        self.move(vel)
        
class Meteor(Object):
    GRAVITY = 1
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size, "meteor")
        self.rect = pygame.Rect(random.randint(-HEIGHT, HEIGHT), random.randint(-100, -64), size, size)
        self.image.blit(get_meteor(size), (0,0))
        self.y_vel = 0
        self.fall_count = 0
        self.mask = pygame.mask.from_surface(self.image)

    def move(self, dy):
        self.rect.y += dy

    def loop(self, fps):
        if self.y_vel == 0:
            self.y_vel += self.GRAVITY * 8 * (self.fall_count // fps)
            self.fall_count += 1
        elif self.rect.y > WIDTH + 100:
            self.fall_count = 0
            
        self.move(self.y_vel)
        pygame.display.update(self.rect)

def get_meteor(size):
    rect = pygame.Rect(0, 0, size, size)
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    image = pygame.image.load(join("assets", "meteor.png"))
    surface.blit(image, (0, 0), rect)

    return  pygame.transform.scale2x(surface)

'''
class Enemies(pygame.sprite.Sprite):
    ANIMATION_DELAY = 3
    
    def __init__(self, x, y, width, height, name):
        self.coordinate = (x , y)
        self.rect = pygame.Rect(x , y, width, height)
        self.name = load_sprite_sheets("Enemies", name, width, height, True)
        self.mask = None
        self.animation_count = 0
        self.x_vel = 0
        self.reverse_direction = "left"
        self.ENEMIES_VEL = 1


    def move(self, dx):
        self.rect.x += dx

    def move_right(self, vel):
        self.x_vel = vel
        if self.reverse_direction != "left":
            self.reverse_direction = "left"
            self.animation_count = 0

    def move_left(self, vel):
        self.x_vel = -vel
        if self.reverse_direction != "right":
            self.reverse_direction = "right"
            self.animation_count = 0

    def move_generator(self, player):        
        if self.rect.center - player.rect.center < 0:
            self.move_right(self.ENEMIES_VEL)
        elif self.rect.center - player.rect.center > 0:
            self.move_left(self.ENEMIES_VEL)

    def update_sprite(self):
        sprite_sheet = "idle"

        if self.rect.right == self.coordinate[0]:
            sprite_sheet = "appear"
        else:
            sprite_sheet = "idle"

        sprite_sheet_name = f"{sprite_sheet}_{self.reverse_direction}"
        sprites = self.ghost[sprite_sheet_name]
        sprite_index = (self.animation_count // 
                        self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft = (self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, window):
        window.blit(self.sprite, (self.rect.x, self.rect.y))

    def loop(self):
        self.move_generator()
        self.move(self.x_vel)
        self.update_sprite()
'''

# Set the coordinates and image for the background
def get_background(name):
    # Get the image
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    # Get the position to later draw the image
    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i*width, j*height)
            tiles.append(pos)
    return tiles, image

# Main draw to display to the platformer
def draw(window, background, bg_image, player, objects, fires, timer, offset_x, offset_y):
    for tile in background:
        window.blit(bg_image, tile)

    for object in objects:
        object.draw(window, offset_x, offset_y)

    for fire in fires:
        fire.draw(window, offset_x, offset_y)


    global game_active
    if game_active:
        font = pygame.font.Font(join("assets", "8-BIT.ttf"), 25)
        text = font.render("Life: " + str(player.hit_point), False, (0, 0, 0))
        window.blit(text, (20, 30))

        timer_font = pygame.font.Font(join("assets", "8-BIT.ttf"), 25)
        timer_text = timer_font.render(f"{timer:06}", False, (0, 0, 0) )
        timer_rect = timer_text.get_rect(topright = (WIDTH - 10, 30))
        window.blit(timer_text, timer_rect)

    elif not game_active:
        window.fill((0, 0, 0))
        font = pygame.font.Font(join("assets", "8-BIT.ttf"), 50)
        text = font.render(("Game Over"), False, (255, 255, 255))
        text_rect = text.get_rect(center = (WIDTH // 2, HEIGHT // 2))
        
        window.blit(text, text_rect)
        pygame.display.flip()


        window.blit(text, text_rect)
        pygame.display.flip


    
    player.draw(window,offset_x, offset_y)
    pygame.display.update()

def handle_vertical_collision(player, objects, fires, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()

            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()
            
            collided_objects.append(obj)
    for fire in fires:
        if pygame.sprite.collide_mask(player, fire):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()

            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(fire)
    
    return collided_objects

def collided(player, objects, fires, dx):
    player.move(dx, 0)
    player.update()
    collided_objects = []

    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_objects.append(obj)
            break
    for fire in fires:
        if pygame.sprite.collide_mask(player, fire):
            collided_objects.append(fire)
            break

    player.move(-dx, 0)
    player.update()
    return collided_objects

# Handlebar (Keybind) setting
def handle_move(player, objects, fires, sfx):
    keys = pygame.key.get_pressed()
    player.x_vel = 0
    collided_left = collided(player, objects, fires , - PLAYER_VEL * 2)
    collided_right = collided(player, objects, fires, PLAYER_VEL * 2)
    

    if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and not collided_left and game_active:
        player.move_left(PLAYER_VEL)
    elif (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and not collided_right and game_active:
        player.move_right(PLAYER_VEL)

    vertical_collided = handle_vertical_collision(player, objects, fires, player.y_vel)
    to_check = [*collided_left, *collided_right, *vertical_collided]
    for obj in to_check:
        if obj and (obj.name == "fire" or obj.name == "meteor"):
            player.make_hit()
            pygame.mixer.Sound.play(sfx)
            
def restart_game(player):
    global game_active
    game_active = True
    player.hit = False
    player.hit_point = 3

def respawn(player):
    player.rect.x, player.rect.y = 400, HEIGHT - 64

def random_generator(low, high):
    last_number = None
    new_number = random.randint(low, high)
    if new_number != last_number:
        last_number = new_number
        yield new_number

def main(window):
    clock = pygame.time.Clock()
    # Set variables for the return values from the function
    background, bg_image = get_background("Blue.png")

    pygame.mixer.music.load(join("assets", "BGM", "Loop.wav"))
    pygame.mixer.music.set_volume(0.1)
    pygame.mixer.music.play(-1)
        

    hit_SFX = pygame.mixer.Sound(join("assets", "SFX", "Playful_Hit.wav"))
    die_SFX = pygame.mixer.Sound(join("assets", "SFX", "Playful_Death.wav"))
    pygame.mixer.Sound.set_volume(hit_SFX, 0.1)
    pygame.mixer.Sound.set_volume(die_SFX, 0.2)

    block_size = 96
    meteor_size = 64
    player = Player(400, HEIGHT - block_size, 50, 50)
    fires =[Fire(i*32, HEIGHT - 100, 16, 32) for i in range(-2 ,WIDTH//16 + 1)]
    for fire in fires:
        fire.on()

    '''
    play_button = Button(50, 50, "Play_button.png")
    '''  
    
    
    meteors = [Meteor(i*meteor_size, i*meteor_size, meteor_size) for i in range(random.randint(1,20))]
    meteor_shower = False

    floor = [Block(i*block_size, HEIGHT - block_size, block_size) for i in range(-1, (500)// block_size)]
    
    block2 = Block(0, HEIGHT - block_size * 2, block_size)
    objects = [*floor, block2, *meteors]
    
    offset_x = 0
    offset_y = 0
    screen_scroll =  -1
    scroll_area_width, scroll_area_height = 200, 50
    
    
    pygame.time.set_timer(pygame.USEREVENT, 1)
    pygame.time.set_timer(pygame.USEREVENT + 1, 100)
    pygame.time.set_timer(pygame.USEREVENT + 2, 500)
    
    counter = 0
    start_tick = pygame.time.get_ticks()

    # Main game's events loop:
    run = True
    while run: 
        # Set the framerate
        clock.tick(FPS)

       
        
        # Quit the game if the "X" button is clicked (part 1)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        
            if game_active:     
                if event.type == pygame.KEYDOWN:
                    if (event.key == pygame.K_SPACE or event.key == pygame.K_UP) and player.jump_count < 2:
                        player.jump()
                        
                if event.type == pygame.USEREVENT:
                    meteor_shower = True

                if event.type == pygame.USEREVENT + 1:
                    offset_y += screen_scroll

                if event.type == pygame.USEREVENT + 2:
                    for j in range(counter, counter + 1):               
                        random_placement = next(random_generator(1,5))
                        
                        if elapsed_time <= 4:
                            more_meteor = [Meteor((i+random_placement)*block_size, HEIGHT - block_size*2*j, block_size) for i in range(0 , next(random_generator(1,2)))]
                            meteors += more_meteor
                        
                        flying_plat = [Block((i+random_placement)*block_size, HEIGHT - block_size*2*j, block_size) for i in range(0 , next(random_generator(1,2)))]
                    objects += flying_plat 
                    print("work")
                    
                    for meteor in meteors:
                        objects.append(meteor)
                    counter += 1
               
        restart_key = pygame.key.get_pressed()

        if meteor_shower:
            for meteor in meteors:
                meteor.loop(FPS)
            meteor_shower = False

        
        if not game_active:
            pygame.mixer.music.pause()
            pygame.mixer.Sound.set_volume(hit_SFX, 0)
            fires = []

            if restart_key[pygame.K_q]:
                restart_game(player)
                respawn(player)
                offset_y = 7
                screen_scroll = 0
                fires =[Fire(i*16, HEIGHT, 16, 32) for i in range(-2, WIDTH//16 + 1)]

                pygame.mixer.music.play()
                pygame.mixer.Sound.set_volume(hit_SFX, 0.2)

        # Update the player's movement 
        player.loop(FPS)
        for fire in fires:
            fire.loop(screen_scroll//6)
        handle_move(player, objects, fires, hit_SFX)

        # Timer in second
        if game_active:
            elapsed_time = (pygame.time.get_ticks() - start_tick)//1000
        else:
            elapsed_time = 0
            start_tick = pygame.time.get_ticks() 

        screen_scroll = -math.log(elapsed_time + 1)*2
        
        # Initiate draw function to draw background
        draw(window, background, bg_image, player, objects, fires, elapsed_time, offset_x, offset_y)

        
        if (((player.rect.right - offset_x) >= (WIDTH - scroll_area_width)) and player.x_vel > 0) or (
            player.rect.left - offset_x <= scroll_area_width and player.x_vel < 0):
            offset_x += player.x_vel

        if (player.rect.y <= scroll_area_height and player.y_vel < 0) or (player.rect.y >= HEIGHT - scroll_area_height and player.y_vel > 0):
            offset_y += player.y_vel*0     

    # Quit the game if the "X" button is clicked (part 2)
    pygame.quit()
    


# Open the game platform only if the code in this file is run
if __name__ == "__main__":
    main(window)