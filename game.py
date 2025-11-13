import pygame
import time
import json

from pygame.locals import *
from time import sleep

class Sprite:
    def __init__(self, x, y, w, h, image):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.speed = 1
        self.image = pygame.image.load(image)
        
    def collides_with(self, other):
        return not(self.x + self.w <= other.x or
                  self.x >= other.x + other.w or
                  self.y + self.h <= other.y or
                  self.y >= other.y + other.h)

    def draw(self, g, scroll_pos_x):
        # Scale the current image to (w, h)
        image = pygame.transform.scale(self.image, (self.w, self.h))
        # Draw it at the correct position, adjusted by scroll
        g.blit(image, (self.x - scroll_pos_x, self.y))

    def is_brick(self):
        return False
        
    def is_luigi(self):
        return False
        
    def is_mushroom(self):
        return False
        
    def is_goomba(self):
        return False
        
    def is_dry_bones(self):
        return False
        
    def is_fireball(self):
        return False

class Brick(Sprite):
    def __init__(self, x, y, w, h, image):
        super().__init__(x, y, w, h, image)
        
    def is_brick(self):
        return True
        
    def update(self):
        pass

class Mushroom(Sprite):
    def __init__(self, x, y, w, h, img_url):
        super().__init__(x, y, w, h, img_url)
        self.vert_velocity = 2.2
        
    def is_mushroom(self):
        return True
        
    def update(self):
        self.y += self.vert_velocity
        if self.y > 500:
            self.y = 500
            self.vert_velocity = 0
            
    def collision(self, s):
        if self.y + self.h >= s.y:
            self.y = s.y - self.h
            self.vert_velocity = 0

class Goomba(Sprite):
    def __init__(self, x, y, w, h, img_url):
        super().__init__(x, y, w, h, img_url)
        self.vert_velocity = 0
        self.velocity_x = 1.5
        self.on_fire = False
        self.fire_counter = 0
        self.collided = False
        self.collided2 = False
        self.collision_direction = None # left or right collision
        self.normal_image = pygame.image.load(img_url)  # Store the normal image
        self.fire_image = pygame.image.load("images/goomba_fire.png")  # Load fire image
        
    def is_goomba(self):
        return True
        
    def set_collided(self, c):
        self.collided = c
        
    def set_collided2(self, c2):
        self.collided2 = c2
        
    def update(self):
        self.vert_velocity += 2.2
        self.y += self.vert_velocity
        if self.collided:
            self.vert_velocity = 0
            self.x += self.velocity_x
        if self.collided2:
            if self.collision_direction == "left":
                self.velocity_x = -abs(self.velocity_x)  # move left
                self.x += self.velocity_x
            elif self.collision_direction == "right":
                self.velocity_x = abs(self.velocity_x)  # move right
                self.x += self.velocity_x
            self.vert_velocity = 0
            self.collided2 = False
            self.collision_direction = None
        if self.fire_counter > 0:
            self.fire_counter -= 1
        

    def collision(self, b):
        top_c = (self.y + self.h >= b.y and self.y < b.y)
        left_side = (self.x + self.w >= b.x and self.x < b.x)
        right_side = (self.x <= b.x + b.w and (self.x + self.w) > (b.x + b.w))

        if top_c:
            # Top collision with brick
            self.y = b.y - self.h
            self.vert_velocity = 0
            # Set collided to true to stop falling through the brick
            self.set_collided(True)
        elif (self.y + self.h > b.y and (self.y < b.y + b.h)):
            if left_side:
                # Left side collision with brick
                self.set_collided2(True)
                self.collision_direction = "left"
            elif right_side:
                # Right side collision with brick
                self.set_collided2(True)
                self.collision_direction = "right"

    def catch_fire(self):
        if not self.on_fire:
            self.on_fire = True
            self.fire_counter = 60
            self.velocity_x = 0 
            self.image = self.fire_image  # Change to fire image

    def disappear(self):
        if self.fire_counter == 1:
            return True
        return False

class DryBones(Sprite):
    def __init__(self, x, y, w, h, img_url):
        super().__init__(x, y, w, h, img_url)
        self.vert_velocity = 0
        self.velocity_x = -1.5
        self.collided = False
        self.collided2 = False  # left or right collision
        self.knock_out = False
        self.knock_out_counter = 0
        self.frame_counter = 0
        self.flip = False
        self.images = []
        self.image_num = 0
        
        # Create and load all images upfront
        for i in range(1, 12):
            img = pygame.image.load(f"images/drybones{i}.png")
            self.images.append(img)
        self.image = self.images[0]  # Set initial image
        
    def is_dry_bones(self):
        return True
        
    def set_collided(self, c):
        self.collided = c
        
    def set_collided2(self, c2):
        self.collided2 = c2
        
    def knocked(self):
        if not self.knock_out:
            self.knock_out = True
            self.image = self.images[10]
            self.knock_out_counter = 180
            
    def update(self):
        self.vert_velocity += 2.2
        self.y += self.vert_velocity
        if self.collided:
            self.vert_velocity = 0
            self.x += self.velocity_x
        if self.collided2:
            self.velocity_x = -self.velocity_x
            self.x += self.velocity_x
            self.vert_velocity = 0
            self.collided2 = False
            self.flip = not self.flip
        if self.knock_out:
            self.knock_out_counter -= 1
            self.velocity_x = 0
            self.x += self.velocity_x
            if self.knock_out_counter == 0:
                self.knock_out = False
                self.image_num = 0
                self.image = self.images[self.image_num]

                if not self.flip:
                    self.velocity_x = -1.5
                else:
                    self.velocity_x = 1.5
                self.x += self.velocity_x
        
        self.frame_counter += 1
        if not self.knock_out and self.frame_counter % 3 == 0:
            self.image_num += 1
            if self.image_num >= 11-3:
                self.image_num = 0
            self.image = self.images[self.image_num]  # Update current image

    def collision(self, b):
        top_c = self.y + self.h >= b.y and self.y < b.y
        left_side = self.x + self.w >= b.x and self.x < b.x
        right_side = self.x <= b.x + b.w and self.x + self.w > b.x + b.w

        if top_c:
            self.y = b.y - self.h
            self.vert_velocity = 0
            self.set_collided(True)
        elif self.y + self.h > b.y and self.y < b.y + b.h:
            if left_side:
                self.x = b.x - self.w
                self.set_collided2(True)
            elif right_side:
                self.x = b.x + b.w
                self.set_collided2(True)
                
    def draw(self, g, scroll_pos_x):
        if self.image:
            scaled_image = pygame.transform.scale(self.image, (self.w, self.h))
            if not self.flip:
                g.blit(scaled_image, (self.x - scroll_pos_x, self.y))
            else:
                flipped_image = pygame.transform.flip(scaled_image, True, False)
                g.blit(flipped_image, (self.x - scroll_pos_x, self.y))

class Fireball(Sprite):
    def __init__(self, x, y, w, h, img_url):
        super().__init__(x, y, w, h, img_url)
        self.vert_velocity = 2.2
        self.velocity_x = 15
        
    def is_fireball(self):
        return True
    
    # def collision(self, b):
    #     if self.y + self.h >= b.y and self.vert_velocity > 0:  # top side collision
    #         self.y = b.y - self.h
    #         self.vert_velocity = 0
    #     elif self.y <= b.y + b.h and self.y > b.y and self.vert_velocity < 0:  # bottom side collision 
    #         self.y = b.y + b.h
    #         self.vert_velocity = 0
    #         print("Hit the bottom of the brick!")
    #     elif self.x <= b.x + b.w and self.x + self.w > b.x + b.w:  # right side collision
    #         self.x = b.x + b.w
    #         print("Hit the right side of the brick!")
    #     elif self.x + self.w >= b.x and self.x < b.x:  # left side collision
    #         self.x = b.x - self.w
    #         print("Hit the left side of the brick!")
    
        
    def update(self):
        self.x += self.velocity_x
        self.y += self.vert_velocity
        if self.y + self.h >= 400:
            self.vert_velocity += -6
        self.vert_velocity += 2

class Luigi(Sprite):
    def __init__(self, x, y, w, h, img_url):
        super().__init__(x, y, w, h, img_url)
        self.vert_velocity = 0
        self.velocity_x = 0
        self.is_jumping = False
        self.is_moving = False
        self.eat_mush = False
        self.frame_counter = 0
        self.jump_counter = 0
        self.image_num = 0
        self.images = []
        
        # Create and load all images upfront
        for i in range(1, 6):
            img = pygame.image.load(f"images/luigi{i}.png")
            self.images.append(img)
        self.image = self.images[0]  # Set initial image
        
    def is_luigi(self):
        return True
        
    def move_right(self):
        self.velocity_x = 5.5
        self.is_moving = True
        
    def move_left(self):
        self.velocity_x = -5.5
        self.is_moving = True
        
    def stop(self):
        self.velocity_x = 0
        self.is_moving = False
        self.image_num = 0
        self.image = self.images[self.image_num]
        
    def jump(self):
        if not self.is_jumping:
            self.vert_velocity = -21
        self.is_jumping = True
        
    def update(self):
        self.vert_velocity += 2.2
        self.y += self.vert_velocity
        self.x += self.velocity_x
        self.x = max(0, min(self.x, 2000 - self.w))  # keep within bounds

        if self.y + self.h < 500:
            self.jump_counter += 1
        else:
            self.jump_counter = 0

        if self.is_moving:
            self.frame_counter += 1
            if self.frame_counter >= 6:
                self.image_num = (self.image_num + 1) % 5  # Luigi has 5 images total
                self.frame_counter = 0
                self.image = self.images[self.image_num]
        else:
            self.image_num = 0
            self.image = self.images[self.image_num]
        
        if self.y + self.h >= 500:
            self.y = 500 - self.h
            self.vert_velocity = 0
            self.is_jumping = False
            self.jump_counter = 0
            
    def collision(self, b):
        if self.y + self.h >= b.y and self.vert_velocity > 0:  # top side collision
            self.y = b.y - self.h
            self.vert_velocity = 0
            self.is_jumping = False
        elif self.y <= b.y + b.h and self.y > b.y and self.vert_velocity < 0:  # bottom side collision 
            self.y = b.y + b.h
            self.vert_velocity = 0
            print("Hit the bottom of the brick!")
        elif self.x <= b.x + b.w and self.x + self.w > b.x + b.w:  # right side collision
            self.stop()
            self.x = b.x + b.w
            print("Hit the right side of the brick!")
        elif self.x + self.w >= b.x and self.x < b.x:  # left side collision
            self.stop()
            self.x = b.x - self.w
            print("Hit the left side of the brick!")
            
    def eat_mushroom(self):
        if not self.eat_mush:
            self.y = self.y + self.h - 25
            self.h = 25
            self.eat_mush = True
        else:
            self.y = self.y + self.h - 50
            self.h = 50
            self.eat_mush = False

class Model:
    def __init__(self):
        self.sprites = []
        for i in range(28):
            self.sprites.append(Brick((i-10)*50, 450, 50, 50, "images/Brick.png"))
        
        with open("map.json") as file:
            data = json.load(file)
            bricks = data["bricks"]
            Drybones = data["drybones"]
            Mushrooms = data["mushrooms"]
            Goombas = data["goombas"]
        file.close()

        for entry in bricks:
            self.sprites.append(Brick(entry["x"], entry["y"], entry["w"], entry["h"], "images/Brick.png"))
        for entry in Drybones:
            self.sprites.append(DryBones(entry["x"], entry["y"], entry["w"], entry["h"], "images/drybones1.png"))
        for entry in Mushrooms:
            self.sprites.append(Mushroom(entry["x"], entry["y"], entry["w"], entry["h"], "images/mushroom.png"))   
        for entry in Goombas:
            self.sprites.append(Goomba(entry["x"], entry["y"], entry["w"], entry["h"], "images/goomba.png"))
        
        # Add player
        self.luigi = Luigi(100, 50, 25, 50, "images/luigi1.png")
        self.sprites.append(self.luigi)
        
    def update(self):
        # Create a copy of sprites to iterate safely
        sprites_to_update = self.sprites.copy()
        
        for sprite in sprites_to_update:
            sprite.update()
        
        for i in range(len(self.sprites)):
            for s in range(len(self.sprites)):
                if i != s and i < len(self.sprites) and s < len(self.sprites) and self.sprites[i].collides_with(self.sprites[s]):
                    if self.sprites[i].is_luigi() and self.sprites[s].is_brick():
                        self.luigi.collision(self.sprites[s])
                    elif self.sprites[i].is_luigi() and self.sprites[s].is_dry_bones():
                        self.sprites[s].knocked()
                    elif self.sprites[i].is_mushroom() and self.sprites[s].is_brick():
                        self.sprites[i].collision(self.sprites[s])
                    elif self.sprites[i].is_goomba() and self.sprites[s].is_brick():
                        self.sprites[i].collision(self.sprites[s])
                    elif self.sprites[i].is_goomba() and self.sprites[s].is_fireball():
                        self.sprites[i].catch_fire()
                        self.remove_sprite(s)  # Remove fireball after hitting
                    elif self.sprites[i].is_dry_bones() and self.sprites[s].is_brick():
                        self.sprites[i].collision(self.sprites[s])
                    elif self.sprites[i].is_dry_bones() and self.sprites[s].is_fireball():
                        self.sprites[i].knocked()
                        self.remove_sprite(s)  # Remove fireball after hitting
                    elif self.sprites[i].is_luigi() and self.sprites[s].is_mushroom():
                        self.luigi.eat_mushroom()
                        self.remove_sprite(s)
        
        # Check for sprites that need to be removed
        for s in range(len(self.sprites)-1, -1, -1):
            if s < len(self.sprites):  # Make sure we're still in bounds
                if self.sprites[s].is_fireball():
                    if self.sprites[s].x > self.luigi.x + 600 or self.sprites[s].x < self.luigi.x - 100:
                        self.remove_sprite(s)
                elif self.sprites[s].is_goomba():
                    if hasattr(self.sprites[s], 'disappear') and self.sprites[s].disappear():
                        self.remove_sprite(s)
                        
    def fireball(self):
        self.sprites.append(Fireball(self.luigi.x, self.luigi.y, 15, 15, "images/fireball.png"))
        
    def remove_sprite(self, ind):
        if 0 <= ind < len(self.sprites):
            self.sprites.pop(ind)

class View:
    def __init__(self, model):
        self.model = model
        self.canvas = pygame.display.set_mode((1000, 500))
        pygame.display.set_caption("Lugi's final resting place, python")
        self.scroll_x = 0
    
    def set_edit_info(self, editMode, addMapItem, removeMapItem, current_item):
        self.editMode = editMode
        self.addMapItem = addMapItem
        self.removeMapItem = removeMapItem
        self.current_item = current_item
        
    def update(self):
        # Clear the screen
        self.canvas.fill((135, 206, 235))  # Sky blue background
        
        # Draw ground
        pygame.draw.rect(self.canvas, (0, 128, 0), (0, 475, 1000, 25))
        
        # Draw all sprites
        for sprite in self.model.sprites:
            sprite.draw(self.canvas, self.scroll_x)
            
        # Update the display
        pygame.display.flip()
        if self.editMode:
            color = (0, 255, 0) if self.addMapItem else (255, 0, 0)
            pygame.draw.rect(self.canvas, color, (0, 0, 100, 100))
            font = pygame.font.SysFont(None, 24)
            label = font.render(self.current_item, True, (0, 0, 0))
            self.canvas.blit(label, (10, 10))
        
    def set_scroll_x(self, i):
        self.scroll_x = max(0, i)  # Prevent negative scrolling

class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.key_right = False
        self.key_left = False
        self.key_up = False
        self.key_down = False
        self.keep_going = True

        self.editMode = False
        self.addMapItem = True
        self.removeMapItem = False
        self.current_item = ["brick", "mushroom", "goomba", "drybones", "fireball"]
        self.current_item_index = 0
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.keep_going = False
                return False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE or event.key == K_q:
                    self.keep_going = False
                elif event.key == K_RIGHT:
                    self.key_right = True
                elif event.key == K_LEFT:
                    self.key_left = True
                elif event.key == K_SPACE or event.key == K_UP:
                    self.key_up = True
                elif event.key == K_DOWN:
                    self.model.fireball()
                elif event.key == K_e:
                    self.editMode = not self.editMode
                    print("e has been pressed.")
                    if(self.editMode):
                        addMapItem = True
                        removeMapItem = False
                    else:
                        addMapItem = False
                        removeMapItem = False
                    if event.key == K_a:
                        print("a has been pressed.")
                        if self.editMode:
                            self.addMapItem = True
                            self.removeMapItem = False
                    if event.key == K_r:
                        print("r has been pressed.")
                        if self.editMode:
                            self.addMapItem = False
                            self.removeMapItem = True                 
            elif event.type == KEYUP:
                if event.key == K_RIGHT:
                    self.key_right = False
                elif event.key == K_LEFT:
                    self.key_left = False
                elif event.key == K_SPACE or event.key == K_UP:
                    self.key_up = False
                
        return True
        
    def update(self):
        if self.key_right:
            self.model.luigi.move_right()
            self.view.set_scroll_x(self.model.luigi.x - 200)
        elif self.key_left:
            self.model.luigi.move_left()
            self.view.set_scroll_x(self.model.luigi.x - 200)
        else:
            self.model.luigi.stop()
        if self.key_up:
            self.model.luigi.jump()
        self.view.set_edit_info(self.editMode, self.addMapItem, self.removeMapItem, self.current_item[self.current_item_index])


print("Use the arrow keys to move. Press Esc to quit.")
pygame.init()
m = Model()
v = View(m)
c = Controller(m, v)
clock = pygame.time.Clock()

while c.keep_going:
    c.handle_events()
    c.update()
    m.update()
    v.update()
    clock.tick(30)
print("Goodbye")