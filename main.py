__author__ = "Julia Zhou"
__version__ = "4/23/2025"

#Flint sessions:
'''https://app.flintk12.com/activities/pygame-debug-le-1fe068/sessions/313103ee-21ed-4071-b4d7-32e3f5f69e5f
https://app.flintk12.com/activities/pygame-debug-le-1fe068/sessions/c39e34ec-65da-4850-bbc4-7afe25b4145a
https://app.flintk12.com/activities/pygame-debug-le-1fe068/sessions/caff70c9-c625-4b4f-ab63-4bd914178fd6
https://app.flintk12.com/activities/pygame-debug-le-1fe068/sessions/6be011fe-b02d-457e-8627-abbff0f38b3f
https://app.flintk12.com/activities/pygame-debug-le-1fe068/sessions/b338d708-258d-4a0e-86d5-9173e4b3ac50
'''

import pygame
import os
from ads import *
from video import *
from transition import *
from spikes import *
from secrets import *
from gameover import *

pygame.mixer.init()
sounds = {
        'glitch':
            pygame.mixer.Sound('sounds/glitch_sound.wav'),
        'spikes':
            pygame.mixer.Sound('sounds/spike_death.wav'),
        'background':
            pygame.mixer.Sound('sounds/Jeremy Blake - Powerup!.wav')
    }

sounds['glitch'].set_volume(0.1)
sounds['spikes'].set_volume(0.3)
sounds['background'].set_volume(0.2)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


class Player(pygame.sprite.Sprite):
    """
    This class represents the bar at the bottom that the player controls.
    """

    # -- Methods
    def __init__(self):
        """ Constructor function """

        # Call the parent's constructor
        super().__init__()

        # Create an image of the block, and fill it with a color.
        # This could also be an image loaded from the disk.
        width = 25
        height = 40
        self.image = pygame.Surface([width, height])
        self.image.fill(RED)

        # Set a reference to the image rect.
        self.rect = self.image.get_rect()

        # Set speed vector of player
        self.change_x = 0
        self.change_y = 0

        # List of sprites we can bump against
        self.level = None

    def update(self):
        """ Move the player. """
        # Gravity
        self.calc_grav()

        # Move left/right
        self.rect.x += self.change_x

        # See if we hit anything
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
            # If we are moving right,
            # set our right side to the left side of the item we hit
            if self.change_x > 0:
                self.rect.right = block.rect.left
            elif self.change_x < 0:
                # Otherwise if we are moving left, do the opposite.
                self.rect.left = block.rect.right

        # Check for hazard collisions
        hazard_hit_list = pygame.sprite.spritecollide(self, self.level.hazard_list, False)
        if len(hazard_hit_list) > 0:
            # Player hit a hazard - respawn instead of quitting
            sounds['spikes'].play()
            self.respawn()

        # Check for ad collisions
        ad_hit_list = pygame.sprite.spritecollide(self, self.level.ad_list, False)
        for ad in ad_hit_list:
            if not hasattr(ad, 'blocked') or not ad.blocked:
                # Block the ad instead of removing it
                ad.block_ad()

                # Increment the counter
                self.level.ads_blocked += 1
                sounds['glitch'].play()


        # Move up/down
        self.rect.y += self.change_y

        # Check and see if we hit anything
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:

            # Reset our position based on the top/bottom of the object.
            if self.change_y > 0:
                self.rect.bottom = block.rect.top
            elif self.change_y < 0:
                self.rect.top = block.rect.bottom

            # Stop our vertical movement
            self.change_y = 0

        if hasattr(self.level, 'secret_list') and hasattr(self.level, 'secret_manager') and self.level.secret_manager:
            secret_hit_list = pygame.sprite.spritecollide(self, self.level.secret_list, False)
            for secret in secret_hit_list:
                if not secret.collected:
                    # Mark the secret as collected
                    secret.collected = True
                    # Let the secret manager handle it
                    if self.level.secret_manager.collect_secret(secret.secret_type):
                        # Make it semi-transparent to show it's been collected
                        secret.image.set_alpha(100)

        standing_on_platform = False
        for platform in self.level.platform_list:
            if isinstance(platform, MovingPlatform):
                # Check if we're standing on this platform
                if (self.rect.bottom == platform.rect.top and
                        self.rect.right > platform.rect.left and
                        self.rect.left < platform.rect.right):
                    # Move with the platform
                    self.rect.x += platform.change_x
                    standing_on_platform = True

                    # If platform is moving up, move player up too
                    if platform.change_y < 0:
                        self.rect.y += platform.change_y



    def respawn(self):
        """Respawn the player at the beginning of the current level"""
        # Reset player position based on level name
        if isinstance(self.level, Level_01):  # Level 1
            self.rect.x = 340
            self.rect.y = SCREEN_HEIGHT - self.rect.height
        elif isinstance(self.level, Level_02):  # Level 2
            self.rect.x = 200
            self.rect.y = 300
        elif isinstance(self.level, Level_03):  # Level 3
            self.rect.x = 200
            self.rect.y = 450
        else:  # Default
            self.rect.x = 340
            self.rect.y = SCREEN_HEIGHT - self.rect.height

        # Reset player movement
        self.change_x = 0
        self.change_y = 0

        # Reset world shift to beginning of level
        self.level.world_shift = 0

        # Reset text object positions to their original screen positions
        for text_obj in self.level.level_text_objects:
            text_obj['rect'].x = text_obj['original_x']
            text_obj['rect'].y = text_obj['original_y']

        # Reset all objects to their original positions
        for platform in self.level.platform_list:
            platform.rect.x = platform.original_x
            platform.rect.y = platform.original_y

        for hazard in self.level.hazard_list:
            hazard.rect.x = hazard.original_x
            hazard.rect.y = hazard.original_y

        for ad in self.level.ad_list:
            ad.rect.x = ad.original_x
            ad.rect.y = ad.original_y

        for video in self.level.video_list:
            video.rect.x = video.original_x
            video.rect.y = video.original_y

        if hasattr(self.level, 'secret_list'):
            for secret in self.level.secret_list:
                secret.rect.x = secret.original_x
                secret.rect.y = secret.original_y

    def calc_grav(self):
        """ Calculate effect of gravity. """
        if self.change_y == 0:
            self.change_y = 1
        else:
            self.change_y += .4

        # See if we are on the ground.
        if self.rect.y >= SCREEN_HEIGHT - self.rect.height and self.change_y >= 0:
            self.change_y = 0
            self.rect.y = SCREEN_HEIGHT - self.rect.height

    def jump(self):
        """ Called when user hits 'jump' button. """

        # move down a bit and see if there is a platform below us.
        # Move down 2 pixels because it doesn't work well if we only move down 1
        self.rect.y += 2
        platform_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        self.rect.y -= 2.5

        # If it is ok to jump, set our speed upwards
        if len(platform_hit_list) > 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.change_y = -10

    # Player-controlled movement:
    def go_left(self):
        """ Called when the user hits the left arrow. """
        self.change_x = -6

    def go_right(self):
        """ Called when the user hits the right arrow. """
        self.change_x = 6

    def stop(self):
        """ Called when the user lets off the keyboard. """
        self.change_x = 0

class Platform(pygame.sprite.Sprite):
    """ Platform the user can jump on """

    def __init__(self, width, height):
        """ Platform constructor. Assumes constructed with user passing in
            an array of 5 numbers like what's defined at the top of this code.
            """
        super().__init__()

        self.image = pygame.Surface([width, height])
        self.image.fill(WHITE)

        self.rect = self.image.get_rect()


class MovingPlatform(Platform):
    """ This is a fancier platform that can actually move. """
    change_x = 0
    change_y = 0

    boundary_top = 0
    boundary_bottom = 0
    boundary_left = 0
    boundary_right = 0

    player = None

    level = None

    def update(self):
        """ Move the platform.
            If the player is in the way, it will shove the player
            out of the way. This does NOT handle what happens if a
            platform shoves a player into another object. Make sure
            moving platforms have clearance to push the player around
            or add code to handle what happens if they don't. """

        # Move left/right
        self.rect.x += self.change_x

        # See if we hit the player
        hit = pygame.sprite.collide_rect(self, self.player)
        if hit:
            # We did hit the player. Shove the player around and
            # assume he/she won't hit anything else.

            # If we are moving right, set our right side
            # to the left side of the item we hit
            if self.change_x < 0:
                self.player.rect.right = self.rect.left
            else:
                # Otherwise if we are moving left, do the opposite.
                self.player.rect.left = self.rect.right

        # Move up/down
        self.rect.y += self.change_y

        # Check and see if we the player
        hit = pygame.sprite.collide_rect(self, self.player)
        if hit:
            # We did hit the player. Shove the player around and
            # assume he/she won't hit anything else.

            # Reset our position based on the top/bottom of the object.
            if self.change_y < 0:
                self.player.rect.bottom = self.rect.top
            else:
                self.player.rect.top = self.rect.bottom

        # Check the boundaries and see if we need to reverse
        # direction.
        if self.rect.bottom > self.boundary_bottom or self.rect.top < self.boundary_top:
            self.change_y *= -1

        if self.rect.x < self.boundary_left + self.level.world_shift or self.rect.x > self.boundary_right + self.level.world_shift:
            self.change_x *= -1


class Hazard(pygame.sprite.Sprite):
    def __init__(self, width, height):
        super().__init__()

        # Load the original image
        image_path = os.path.join('img', "glitch.png")
        original_image = pygame.image.load(image_path).convert_alpha()


        # Create a surface of the desired size
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)

        # Tile the original image across the surface
        for x in range(0, width, original_image.get_width()):
            for y in range(0, height, original_image.get_height()):
                self.image.blit(original_image, (x, y))

        self.rect = self.image.get_rect()


class Level():
    """ This is a generic super-class used to define a level.
        Create a child class for each level with level-specific
        info. """

    def __init__(self, player, screen=None):
        """ Constructor. Pass in a handle to player. Needed for when moving
            platforms collide with the player. """
        self.platform_list = pygame.sprite.Group()
        self.enemy_list = pygame.sprite.Group()
        self.hazard_list = pygame.sprite.Group()
        self.player = player
        self.ad_list = pygame.sprite.Group()
        self.total_ads = 0  # Will be set when ads are added
        self.ads_blocked = 0  # Counter for blocked ads
        self.message = None
        self.video_message_timer = 0

        self.video_list = pygame.sprite.Group()
        self.secret_list = pygame.sprite.Group()
        self.secret_manager = None

        # Explicitly set the screen attribute
        self.screen = screen

        # Initialize level text list
        self.level_text = []

        # Store level text as objects with position tracking
        self.level_text_objects = []

        # How far this world has been scrolled left/right
        self.world_shift = 0

    def draw_text(self, text, x, y, size=24, color=(255, 255, 255)):
        """Create a text object that can be tracked and shifted"""
        if self.screen is not None:
            font = pygame.font.SysFont('Arial', size)
            text_surface = font.render(text, True, color)
            text_rect = text_surface.get_rect(center=(x, y))

            # Store the text object with its surface and rect
            text_obj = {
                'surface': text_surface,
                'rect': text_rect,
                'original_x': text_rect.x,  # Store original x for reference
                'original_y': text_rect.y  # Store original y for reference
            }
            self.level_text_objects.append(text_obj)

    def update(self):
        """ Update everything in this level."""
        self.platform_list.update()
        self.enemy_list.update()
        self.ad_list.update()
        self.video_list.update()

        # Update message timer if active
        if self.message:
            self.message['timer'] -= 1
            if self.message['timer'] <= 0:
                self.message = None

    def draw(self, screen):
        screen.fill(BLACK)
        self.platform_list.draw(screen)
        self.enemy_list.draw(screen)
        self.hazard_list.draw(screen)
        self.ad_list.draw(screen)
        self.video_list.draw(screen)
        self.secret_list.draw(screen)

        # Draw stored text objects
        for text_obj in self.level_text_objects:
            screen.blit(text_obj['surface'], text_obj['rect'])

        # Draw message if active
        if self.message:
            screen.blit(self.message['surface'], self.message['rect'])

        if self.secret_manager:
            font = pygame.font.SysFont('Arial', 20)
            total_secrets = self.secret_manager.get_total_collected()
            secrets_text = font.render(f"Secrets: {total_secrets}/3", True, WHITE)
            screen.blit(secrets_text, (10, 10))

    def store_original_positions(self):
        """Store the original positions of all objects for respawning"""
        for platform in self.platform_list:
            platform.original_x = platform.rect.x
            platform.original_y = platform.rect.y

        for hazard in self.hazard_list:
            hazard.original_x = hazard.rect.x
            hazard.original_y = hazard.rect.y

        for ad in self.ad_list:
            ad.original_x = ad.rect.x
            ad.original_y = ad.rect.y

        for video in self.video_list:
            video.original_x = video.rect.x
            video.original_y = video.rect.y

        for secret in self.secret_list:
            secret.original_x = secret.rect.x
            secret.original_y = secret.rect.y

    def shift_world(self, shift_x):
        """ When the user moves left/right and we need to scroll
        everything: """

        # Keep track of the shift amount
        self.world_shift += shift_x

        # Go through all the sprite lists and shift
        for platform in self.platform_list:
            platform.rect.x += shift_x

        for enemy in self.enemy_list:
            enemy.rect.x += shift_x

        for hazard in self.hazard_list:
            hazard.rect.x += shift_x

        for ad in self.ad_list:
            ad.rect.x += shift_x

        for video in self.video_list:
            video.rect.x += shift_x

        for text_obj in self.level_text_objects:
            text_obj['rect'].x += shift_x

        for secret in self.secret_list:
            secret.rect.x += shift_x

        # Create platforms for the level
class Level_01(Level):
    """ Definition for level 1. """

    def __init__(self, player, screen=None):
        """ Create level 1. """

        super().__init__(player, screen)

        self.level_limit = -2800

        # Array with width, height, x, and y of platform
        level = [[210, 15, 500, 500],
                 [210, 15, 800, 400],
                 [230, 15, 1210, 500],
                 [210, 15, 1110, 280],
                 [210, 15, 1540, 200],
                 [230, 15, 1540, 200],
                 [200, 15, 1540, 100],
                 [210, 15, 1820, 150],
                 [340, 15, 2300, 400],
                 [100, 15, 2700, 300],
                 [100, 15, 2850, 200],
                 [60, 15, 3000, 100],
                 [15, 470, 3200, 0],
                 [370, 15, 3130, 540],
                 [80, 15, 3400, 420],
                 [80, 15, 3260, 320],
                 [80, 15, 3500, 200]
                 #[160, 90, 3260, 30]
                 ]

        # Go through the array above and add platforms
        for platform in level:
            block = Platform(platform[0], platform[1])
            block.rect.x = platform[2]
            block.rect.y = platform[3]
            block.player = self.player
            self.platform_list.add(block)

        ad1 = Ads(level_number=1, x=1540, y=10)
        ad2 = Ads(level_number=1, x=1300, y=400)
        self.ad_list.add(ad1)
        self.ad_list.add(ad2)

        self.total_ads = len(self.ad_list)

        hazard = Hazard(4000,20)
        hazard.rect.x = 500
        hazard.rect.y = 580
        self.hazard_list.add(hazard)

        video = Video(3260,30,160,90)
        self.video_list.add(video)

        plat_spikes1 = Spikes(x=1970, y=130, width=60, height=20, color=(100, 0, 255))
        self.hazard_list.add(plat_spikes1)

        plat_spikes2 = Spikes(x=2440, y=380, width=60, height=20, color=(100, 0, 255))
        self.hazard_list.add(plat_spikes2)

        # Vertical spikes (90 degrees rotation)
        vertical_spikes1 = Spikes(x=3180, y=-10, width=480, height=20, angle=90)
        self.hazard_list.add(vertical_spikes1)

        self.draw_text('Level 1', 500, 200, size=36, color=(255, 255, 255))
        self.draw_text('Avoid the glitches and spikes!', 500, 250, size=24, color=(200, 200, 200))

        self.draw_text('Oh wow. A secret!', -1000, 350, size=24, color=(255, 255, 255))
        self.draw_text('I wonder if there are more of these...', -1000, 400, size=16, color=(200, 200, 200))

        silver_secret = Secret(-1120, 450, secret_type=1)
        self.secret_list.add(silver_secret)

class Level_02(Level):
    """ Definition for level 2. """

    def __init__(self, player, screen=None):
        """ Create level 1. """

        # Call the parent constructor
        super().__init__(player, screen)

        self.level_limit = -1000

        # Array with type of platform, and x, y location of the platform.
        level = [[210, 15, 100, 400],
                 [30, 15, 50, 500],
                 [50, 15, 350, 370],
                 [30, 15, 450, 280],
                 [150, 15, 520, 230],
                 [150, 15, 710, 190],
                 [130, 15, 860, 140],
                 [15, 80, 1040, 0], #spikes/glitch
                 [80, 15, 1100, 200],
                 [200, 15, 1300, 90],
                 [15, 315, 1485, 100],
                 [15, 520, 1600, 90]
                 #[1000, 15, 495, 400], #glitch
                 #[15, 200, 480, 400],
                 #[176, 99, 530, 465]
                 ]

        # Go through the array above and add platforms
        for platform in level:
            block = Platform(platform[0], platform[1])
            block.rect.x = platform[2]
            block.rect.y = platform[3]
            block.player = self.player
            self.platform_list.add(block)

        ad1 = Ads(level_number=2, x=150, y=460)
        ad2 = Ads(level_number=2, x=830, y=50)
        ad3 = Ads(level_number=2, x=990, y=500)
        self.ad_list.add(ad1)
        self.ad_list.add(ad2)
        self.ad_list.add(ad3)

        self.total_ads = len(self.ad_list)


        hazard = Hazard(1005, 15)
        hazard.rect.x = 495
        hazard.rect.y = 400
        self.hazard_list.add(hazard)

        hazard = Hazard(15, 200)
        hazard.rect.x = 480
        hazard.rect.y = 400
        self.hazard_list.add(hazard)

        hazard = Hazard(350, 15)
        hazard.rect.x = 1615
        hazard.rect.y = 585
        self.hazard_list.add(hazard)

        video = Video(530, 450, 176,99)
        self.video_list.add(video)

        plat_spikes = Spikes(x=520, y=210, width=60, height=20, color=(100, 0, 255))
        self.hazard_list.add(plat_spikes)

        # Vertical spikes (90 degrees rotation)
        vertical_spikes = Spikes(x=1020, y=0, width=80, height=20, angle=90)
        self.hazard_list.add(vertical_spikes)

        # Floating spike section
        floating_spikes = Spikes(x=990, y=250, width=120, height=20, color=(100, 0, 255))
        self.hazard_list.add(floating_spikes)

        floor_spikes = Spikes(x=1500, y=580, width=100, height=20, color=(100, 0, 255))
        self.hazard_list.add(floor_spikes)

        self.draw_text('Level 2', 200, 150, size=36, color=(255, 255, 255))
        self.draw_text('Same thing as Level 1', 200, 200, size=24, color=(200, 200, 200))

        # Add level text
        self.draw_text('Gold play button!!', 3000, 400, size=24, color=(255, 255, 255))
        self.draw_text('I really should be working on more important parts of this game', 3000, 430, size=16, color=(200, 200, 200))

        gold_secret = Secret(2900, 450,  secret_type=2)
        self.secret_list.add(gold_secret)


class Level_03(Level):
    """ Definition for level 3. """

    def __init__(self, player, screen=None):
        """ Create level 1. """

        super().__init__(player, screen)
        self.level_limit = -1000

        # Array with type of platform, and x, y location of the platform.
        level = [[150, 15, 200, 500],
                 [70, 15, 370, 390],
                 #3[70, 15, 240, 270], #make this moving
                 [70, 15, 350, 190],
                 [15, 360, 500, 175], #glitch/ad spikes
                 [600, 15, 150, 70], #add some glitch
                 [70, 15, 580, 200],
                 #[70, 15, 700, 350], #make this moving
                 [70, 15, 920, 240],
                 [70, 15, 920, 140]
                 #[80, 45, 240, 10]
                 ]

        # Go through the array above and add platforms
        for platform in level:
            block = Platform(platform[0], platform[1])
            block.rect.x = platform[2]
            block.rect.y = platform[3]
            block.player = self.player
            self.platform_list.add(block)

        block = MovingPlatform(70, 15)
        block.rect.x = 240  # Fixed horizontal position
        block.rect.y = 270  # Starting vertical position
        block.boundary_top = 200  # Highest position
        block.boundary_bottom = 350  # Lowest position
        block.change_y = 1  # Vertical speed (positive moves down)
        block.player = self.player
        block.level = self
        self.platform_list.add(block)

        block = MovingPlatform(70, 15)
        block.rect.x = 700
        block.rect.y = 350
        block.boundary_left = 650
        block.boundary_right = 780
        block.change_x = 1
        block.player = self.player
        block.level = self
        self.platform_list.add(block)

        ad1 = Ads(level_number=3, x=90, y=150)
        ad2 = Ads(level_number=3, x=1000, y=40)
        self.ad_list.add(ad1)
        self.ad_list.add(ad2)

        self.total_ads = len(self.ad_list)

        hazard = Hazard(4300, 15)
        hazard.rect.x = -300
        hazard.rect.y = 580
        self.hazard_list.add(hazard)

        video = Video(240, 4,80,45)
        self.video_list.add(video)

        wall_spikes1 = Spikes(x=480, y=175, width=360, height=20, color=(100, 0, 255), angle=90)
        self.hazard_list.add(wall_spikes1)

        wall_spikes2 = Spikes(x=515, y=175, width=360, height=20, color=(100, 0, 255), angle=270)
        self.hazard_list.add(wall_spikes2)

        upside_down_spikes1 = Spikes(x=380, y=85, width=60, height=20, color=(100, 0, 255), angle=180)
        self.hazard_list.add(upside_down_spikes1)

        upside_down_spikes2 = Spikes(x=550, y=85, width=60, height=20, color=(100, 0, 255), angle=180)
        self.hazard_list.add(upside_down_spikes2)

        # Add level text
        self.draw_text('Level 3', 170, 350, size=36, color=(255, 255, 255))
        self.draw_text('I think you get the idea', 170, 400, size=24, color=(200, 200, 200))

        self.draw_text('You know the level\'s that way, right? -->', -700, 450, size=16,color=(200, 200, 200))
        self.draw_text('...okay, if you insist', -1500, 450, size=16, color=(200, 200, 200))
        self.draw_text('Quite the trek, don\'t you think?', -2700, 450, size=16, color=(200, 200, 200))
        self.draw_text('Diamond play button!!! (ʘᗩʘ’)', -4500, 400, size=24, color=(255, 255, 255))
        self.draw_text('How did you find this one??', -4500, 430, size=16, color=(200, 200, 200))

        diamond_secret = Secret(-4605, 460,  secret_type=3)
        self.secret_list.add(diamond_secret)


def main():
    """ Main Program """
    pygame.init()

    secret_manager = SecretManager()

    # Set the height and width of the screen
    size = [SCREEN_WIDTH, SCREEN_HEIGHT]
    screen = pygame.display.set_mode(size)

    if sounds['background']:
        sounds['background'].play(-1)

    pygame.display.set_caption("͓̽A͓͓̽̽d͓͓̽̽B͓͓̽̽l͓̽o͓͓̽̽c͓͓̽̽k͓͓̽̽e͓͓̽̽r͓̽")

    # Create the player
    player = Player()

    # Create all the levels
    level_list = []
    level_list.append(Level_01(player, screen))
    level_list.append(Level_02(player, screen))
    level_list.append(Level_03(player, screen))

    # Store original positions for respawning (only need to do this once)
    for level in level_list:
        level.store_original_positions()
        level.secret_manager = secret_manager

    # Set the current level
    current_level_no = 0
    current_level = level_list[current_level_no]

    active_sprite_list = pygame.sprite.Group()
    player.level = current_level

    player.rect.x = 340
    player.rect.y = SCREEN_HEIGHT - player.rect.height
    active_sprite_list.add(player)

    game_over_screen = None
    show_game_over = False

    # Loop until the user clicks the close button.
    done = False

    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()

    # Transition screen variables
    transition = None
    in_transition = False

    # -------- Main Program Loop -----------
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

            # Handle keyboard input only when not in transition
            if not in_transition:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        player.go_left()
                    if event.key == pygame.K_RIGHT:
                        player.go_right()
                    if event.key == pygame.K_UP:
                        player.jump()

                    # Level selection keys
                    if event.key == pygame.K_1:
                        current_level_no = 0
                        current_level = level_list[current_level_no]
                        player.level = current_level
                        player.rect.x = 340
                        player.rect.y = SCREEN_HEIGHT - player.rect.height
                    if event.key == pygame.K_2:
                        current_level_no = 1
                        current_level = level_list[current_level_no]
                        player.level = current_level
                        player.rect.x = 200
                        player.rect.y = 400
                    if event.key == pygame.K_3:
                        current_level_no = 2
                        current_level = level_list[current_level_no]
                        player.level = current_level
                        player.rect.x = 200
                        player.rect.y = 450

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT and player.change_x < 0:
                        player.stop()
                    if event.key == pygame.K_RIGHT and player.change_x > 0:
                        player.stop()
            # If in transition, check for key press to advance
            elif event.type == pygame.KEYDOWN and transition and transition.state == "display":
                transition.state = "fade_out"


        # Handle transition if active
        if in_transition:
            # Update the game first
            current_level.update()
            active_sprite_list.update()

            # Draw the game
            current_level.draw(screen)
            active_sprite_list.draw(screen)

            # Update and draw transition on top
            transition.draw()
            if transition.update():
                in_transition = False

                # Check if we just completed the final level
                if current_level_no == len(level_list) - 1:
                    # We completed the last level, show game over screen
                    show_game_over = True
                    game_over_screen = GameOver(screen, secret_manager)
                else:
                    # Set up the next level
                    player.rect.x = 120
                    current_level_no += 1
                    current_level = level_list[current_level_no]
                    player.level = current_level
        elif show_game_over:
            # Handle game over screen
            game_over_screen.update()
            game_over_screen.draw()

            # Check for key presses to restart or quit
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                # Reset the game
                show_game_over = False
                current_level_no = 0
                current_level = level_list[current_level_no]
                player.level = current_level
                player.respawn()
            elif keys[pygame.K_q]:
                done = True
        else:
            # Update the player
            active_sprite_list.update()

            # Update items in the level
            current_level.update()

            # Check for video collisions
            # Check for video collisions
            video_hit_list = pygame.sprite.spritecollide(player, current_level.video_list, False)
            if len(video_hit_list) > 0 and not in_transition:
                # Check if all ads have been blocked
                if current_level.ads_blocked >= current_level.total_ads:
                    # Check if this is the final level
                    if current_level_no == len(level_list) - 1:
                        # Final level completed - go directly to game over screen
                        show_game_over = True
                        game_over_screen = GameOver(screen, secret_manager)
                    else:
                        # Not final level - trigger normal transition
                        in_transition = True
                        transition = TransitionScreen(screen, f"Level {current_level_no + 2}")
                else:
                    # Not all ads blocked - show message
                    font = pygame.font.SysFont('Arial', 24)
                    message = f"Block all ads to continue! ({current_level.ads_blocked}/{current_level.total_ads})"
                    text_surface = font.render(message, True, BLUE)
                    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2 + 200, 50))
                    current_level.message = {
                        'surface': text_surface,
                        'rect': text_rect,
                        'timer': 180  # Display for 3 seconds (60 fps * 3)
                    }

            # If the player gets near the right side, shift the world left (-x)
            if player.rect.right >= 500:
                diff = player.rect.right - 500
                player.rect.right = 500
                current_level.shift_world(-diff)

            # If the player gets near the left side, shift the world right (+x)
            if player.rect.left <= 120:
                diff = 120 - player.rect.left
                player.rect.left = 120
                current_level.shift_world(diff)

            # Draw everything
            current_level.draw(screen)
            active_sprite_list.draw(screen)

        # Limit to 60 frames per second
        clock.tick(60)

        # Go ahead and update the screen with what we've drawn.
        pygame.display.flip()

    # Be IDLE friendly. If you forget this line, the program will 'hang'
    # on exit.
    pygame.quit()


if __name__ == "__main__":
    main()