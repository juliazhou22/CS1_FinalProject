import os
import pygame
import random

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


class Ads(pygame.sprite.Sprite):
    # Define spawn points for each level as class variables
    LEVEL1_SPAWN_POINTS = [
        (600, 450),  # Near first platform
        (900, 350),  # Above second platform
        (1300, 450)  # Near third platform
    ]

    LEVEL2_SPAWN_POINTS = [
        (150, 350),  # Near starting area
        (600, 150),  # Above middle platforms
        (1000, 150)  # Near end of level
    ]

    LEVEL3_SPAWN_POINTS = [
        (300, 150),  # Upper area
        (600, 300),  # Middle area
        (800, 200)  # Near moving platform
    ]

    def __init__(self, level_number=1, x=None, y=None):
        pygame.sprite.Sprite.__init__(self)

        # Select spawn points based on level
        if x is not None and y is not None:
            # Use specific coordinates if provided
            spawn_point = (x, y)
        else:
            # Otherwise use level-specific spawn points
            if level_number == 1:
                spawn_points = self.LEVEL1_SPAWN_POINTS
            elif level_number == 2:
                spawn_points = self.LEVEL2_SPAWN_POINTS
            elif level_number == 3:
                spawn_points = self.LEVEL3_SPAWN_POINTS
            else:
                # Default spawn points if level is unknown
                spawn_points = [
                    (200, 300),
                    (400, 200),
                    (600, 400)
                ]

            spawn_point = random.choice(spawn_points)

        # Randomly select an ad image
        item_type = random.randint(1, 5)
        if item_type == 1:
            image_path = os.path.join('img', "ad1.png")
        elif item_type == 2:
            image_path = os.path.join('img', "ad2.png")
        elif item_type == 3:
            image_path = os.path.join('img', "ad3.png")
        elif item_type == 4:
            image_path = os.path.join('img', "ad4.png")
        elif item_type == 5:
            image_path = os.path.join('img', "ad5.png")

        # Load the image
        original_image = pygame.image.load(image_path).convert_alpha()

        # Randomly scale the image
        scale_factor = 0.5
        width = int(original_image.get_width() * scale_factor)
        height = int(original_image.get_height() * scale_factor)

        self.image = pygame.transform.scale(original_image, (width, height))

        self.original_image = self.image.copy()

        # Set the rect and position
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = spawn_point

        # Track if this ad has been blocked
        self.blocked = False

        # Store the original image for reference
        self.original_image = self.image.copy()

    def convert_to_greyscale(self, surface):
        """Convert a surface to greyscale"""
        width, height = surface.get_size()
        greyscale_surface = pygame.Surface((width, height), pygame.SRCALPHA)

        # Process each pixel to convert to greyscale
        for x in range(width):
            for y in range(height):
                pixel = surface.get_at((x, y))
                # Skip fully transparent pixels
                if pixel[3] > 0:  # If not fully transparent
                    # Calculate greyscale value (standard luminance formula)
                    grey_value = int(0.299 * pixel[0] + 0.587 * pixel[1] + 0.114 * pixel[2])
                    greyscale_surface.set_at((x, y), (grey_value, grey_value, grey_value, pixel[3]))

        return greyscale_surface

    def block_ad(self):
        """Mark this ad as blocked and draw the strikethrough circle"""
        if not self.blocked:
            self.blocked = True
            self.draw_strikethrough()
            self.convert_to_greyscale(self.original_image)

    def block_ad(self):
        """Mark this ad as blocked and draw the strikethrough circle"""
        if not self.blocked:
            self.blocked = True

            # First convert to greyscale
            self.image = self.convert_to_greyscale(self.original_image)

            # Then draw the strikethrough on the greyscale image
            self.draw_strikethrough()

    def draw_strikethrough(self):
        """Draw a red circle with a line through it on the ad"""
        # Get dimensions
        width, height = self.image.get_size()
        center_x, center_y = width // 2, height // 2
        radius = min(width, height) // 2

        # Create a new surface for the strikethrough
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)

        # Draw red circle
        pygame.draw.circle(overlay, (255, 0, 0, 180), (center_x, center_y), radius, 3)

        # Draw diagonal line (strikethrough)
        pygame.draw.line(overlay, (255, 0, 0, 180),
                         (center_x - radius * 0.7, center_y - radius * 0.7),
                         (center_x + radius * 0.7, center_y + radius * 0.7),
                         5)

        # Apply the overlay to the image
        self.image.blit(overlay, (0, 0))

    def update(self):
        # Optional: Add some subtle movement
        if not self.blocked:
            self.rect.y += random.randint(-1, 1)
            self.rect.x += random.randint(-1, 1)