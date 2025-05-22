import pygame
import math


class Spikes(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=(255, 0, 0), angle=0):
        """
        Create a row of equilateral triangular spikes with rotation support

        Args:
        - x: x-coordinate of the spikes
        - y: y-coordinate of the spikes
        - width: Total width of the spike row
        - height: Height of individual spikes
        - color: Color of the spikes (default is red)
        - angle: Rotation angle in degrees (default is 0)
        """
        super().__init__()

        # Create a surface with per-pixel alpha
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)

        # Fill with a transparent background first
        self.image.fill((0, 0, 0, 0))

        # Calculate number of spikes based on width
        # Each spike will be an equilateral triangle
        spike_width = height  # Base of the triangle equals height
        num_spikes = width // spike_width

        # Draw each spike
        for i in range(num_spikes + 1):  # +1 to ensure full width coverage
            # Calculate triangle points
            x_offset = i * spike_width
            points = [
                (x_offset, height),  # Bottom left
                (x_offset + spike_width // 2, 0),  # Top middle
                (x_offset + spike_width, height)  # Bottom right
            ]

            # Draw the triangle
            pygame.draw.polygon(self.image, color, points)

        # Rotate the image if angle is not 0
        if angle != 0:
            self.image = pygame.transform.rotate(self.image, angle)

        # Create rect and position it
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        # Optional update method if you want any dynamic behavior
        pass