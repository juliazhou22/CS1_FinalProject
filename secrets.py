import pygame
import os


class Secret(pygame.sprite.Sprite):
    """A secret collectible item that the player can find"""

    def __init__(self, x, y, width=30, height=30, secret_type=1):
        """Initialize the secret collectible

        Args:
            x: X position
            y: Y position
            width: Width of the collectible
            height: Height of the collectible
            secret_type: Type of secret (1, 2, or 3)
        """
        super().__init__()

        # Load different images based on secret type
        if secret_type == 1:
            image_path = os.path.join('img', "silver.png")
            self.name = "Silver Play Button"
        elif secret_type == 2:
            image_path = os.path.join('img', "gold.png")
            self.name = "Gold Play Button"
        elif secret_type == 3:
            image_path = os.path.join('img', "diamond.png")
            self.name = "Diamond Play Button"
        else:
            # Fallback if image not found
            image_path = None
            self.name = "Mystery Button"

        self.original_image = pygame.image.load(image_path).convert_alpha()

        scale_factor = 0.75
        width = int(self.original_image.get_width() * scale_factor)
        height = int(self.original_image.get_height() * scale_factor)
        self.image = pygame.transform.scale(self.original_image, (width, height))

        # Try to load the image
        try:
            if image_path and os.path.exists(image_path):
                # Load the image and scale it to the desired size
                original_image = pygame.image.load(image_path).convert_alpha()
                self.image = pygame.transform.scale(original_image, (width, height))
            else:
                # Fallback to a colored rectangle if image not found
                self.image = pygame.Surface([width, height])

                # Choose color based on secret type
                if secret_type == 1:
                    color = (192, 192, 192)  # Silver
                elif secret_type == 2:
                    color = (255, 215, 0)  # Gold
                elif secret_type == 3:
                    color = (185, 242, 255)  # Diamond blue
                else:
                    color = (255, 255, 255)  # White

                self.image.fill(color)

                # Draw a play button triangle
                pygame.draw.polygon(self.image, (50, 50, 50),
                                    [(width // 4, height // 4),
                                     (width // 4, 3 * height // 4),
                                     (3 * width // 4, height // 2)])
        except Exception as e:
            print(f"Error loading secret image: {e}")
            # Create a fallback surface
            self.image = pygame.Surface([width, height])
            self.image.fill((255, 255, 255))  # White

        # Set the rectangle position
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Store original position for respawning
        self.original_x = x
        self.original_y = y

        # Store the secret type
        self.secret_type = secret_type

        # Flag to track if this secret has been collected
        self.collected = False


class SecretManager:
    """Manages all secrets in the game"""

    def __init__(self):
        """Initialize the secret manager"""
        # Dictionary to track which secrets have been collected
        self.collected_secrets = {1: False, 2: False, 3: False}

        # Sound effect for collecting a secret
        try:
            self.collect_sound = pygame.mixer.Sound('sounds/collect.wav')
            self.collect_sound.set_volume(0.5)
        except:
            self.collect_sound = None
            print("Warning: Could not load secret collection sound")

    def collect_secret(self, secret_type):
        """Mark a secret as collected

        Args:
            secret_type: The type of secret (1, 2, or 3)

        Returns:
            bool: True if this is the first time collecting this secret
        """
        # Check if this secret was already collected
        if not self.collected_secrets.get(secret_type, False):
            # Mark as collected
            self.collected_secrets[secret_type] = True

            # Play sound if available
            if self.collect_sound:
                self.collect_sound.play()

            return True
        return False

    def get_total_collected(self):
        """Get the total number of unique secrets collected

        Returns:
            int: Number of unique secrets collected (0-3)
        """
        return sum(1 for collected in self.collected_secrets.values() if collected)

    def is_collected(self, secret_type):
        """Check if a specific secret has been collected

        Args:
            secret_type: The type of secret (1, 2, or 3)

        Returns:
            bool: True if collected, False otherwise
        """
        return self.collected_secrets.get(secret_type, False)

    def reset(self):
        """Reset all secrets to uncollected state"""
        for key in self.collected_secrets:
            self.collected_secrets[key] = False