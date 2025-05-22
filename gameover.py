import pygame

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

class GameOver:
    def __init__(self, screen, secret_manager=None):
        self.screen = screen
        self.secret_manager = secret_manager
        self.state = "fade_in"
        self.alpha = 0  # Start fully transparent
        self.timer = 0
        self.font_large = pygame.font.SysFont('Arial', 48)
        self.font_medium = pygame.font.SysFont('Arial', 32)
        self.font_small = pygame.font.SysFont('Arial', 24)

        # Create text surfaces
        self.title_text = self.font_large.render("Congratulations!", True, (255, 255, 255))
        self.subtitle_text = self.font_medium.render("You've completed AdBlocker!", True, (200, 200, 200))

        # Create instruction text
        self.restart_text = self.font_small.render("Press 'R' to restart", True, (150, 150, 150))
        self.quit_text = self.font_small.render("Press 'Q' to quit", True, (150, 150, 150))

        # If we have a secret manager, create text for secrets collected
        self.secrets_text = None
        if secret_manager:
            total_secrets = secret_manager.get_total_collected()
            max_secrets = 3  # Assuming there are 3 total secrets
            self.secrets_text = self.font_medium.render(f"Secrets Found: {total_secrets}/{max_secrets}", True,
                                                        (255, 215, 0))

    def update(self):
        # Update the fade effect
        self.timer += 1

        if self.state == "fade_in":
            self.alpha += 3  # Fade in speed
            if self.alpha >= 255:
                self.alpha = 255
                self.state = "display"

        elif self.state == "display":
            # Just display the screen, no updates needed
            pass

        elif self.state == "fade_out":
            self.alpha -= 5  # Fade out speed
            if self.alpha <= 0:
                self.alpha = 0
                return True  # Signal that we're done

        return False  # Not done yet

    def draw(self):
        # Create a black overlay with the current alpha
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(self.alpha)

        # Blit the overlay
        self.screen.blit(overlay, (0, 0))

        # Only draw text if we're visible enough
        if self.alpha > 50:
            # Calculate positions
            title_rect = self.title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
            subtitle_rect = self.subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 60))

            # Set alpha for text
            title_surface = self.title_text.copy()
            title_surface.set_alpha(self.alpha)
            subtitle_surface = self.subtitle_text.copy()
            subtitle_surface.set_alpha(self.alpha)

            # Draw main text
            self.screen.blit(title_surface, title_rect)
            self.screen.blit(subtitle_surface, subtitle_rect)

            # Draw secrets text if available
            if self.secrets_text:
                secrets_surface = self.secrets_text.copy()
                secrets_surface.set_alpha(self.alpha)
                secrets_rect = self.secrets_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
                self.screen.blit(secrets_surface, secrets_rect)

            # Draw instruction text
            restart_surface = self.restart_text.copy()
            restart_surface.set_alpha(self.alpha)
            restart_rect = self.restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4))
            self.screen.blit(restart_surface, restart_rect)

            quit_surface = self.quit_text.copy()
            quit_surface.set_alpha(self.alpha)
            quit_rect = self.quit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4 + 40))
            self.screen.blit(quit_surface, quit_rect)