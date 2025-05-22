import pygame
import os
import random
import math

class Video(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        pygame.sprite.Sprite.__init__(self)

        # Randomly select a video thumbnail
        item_type = random.randint(1, 6)

        if item_type == 1:
            image_path = os.path.join('img', "video1.png")
        elif item_type == 2:
            image_path = os.path.join('img', "video2.png")
        elif item_type == 3:
            image_path = os.path.join('img', "video3.png")
        elif item_type == 4:
            image_path = os.path.join('img', "video4.png")
        elif item_type == 5:
            image_path = os.path.join('img', "video5.png")
        elif item_type == 6:
            image_path = os.path.join('img', "video6.png")

        # Load the image
        self.original_image = pygame.image.load(image_path).convert_alpha()

        # Set rect
        self.image = pygame.transform.scale(self.original_image, (width, height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Store original y for floating movement
        self.original_y = y

        # Variables for floating movement
        self.float_counter = 0
        self.float_speed = 0.05
        self.float_range = 10

    def update(self):
        # Create floating up and down movement
        self.float_counter += self.float_speed
        offset = self.float_range * math.sin(self.float_counter)
        self.rect.y = self.original_y + offset