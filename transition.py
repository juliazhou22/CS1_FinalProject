import pygame


class TransitionScreen:
    def __init__(self, screen, next_level_text):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.next_level_text = next_level_text
        self.font = pygame.font.Font(None, 48)  # Default font, size 48
        self.small_font = pygame.font.Font(None, 24)  # Smaller font for instructions

        # Animation variables
        self.alpha = 0  # Start fully transparent
        self.fade_speed = 10  # Speed of fade in/out
        self.state = 'fade_in'  # States: fade_in, display, fade_out
        self.display_timer = 0
        self.display_duration = 120  # 2 seconds at 60 FPS

    def update(self):
        if self.state == 'fade_in':
            self.alpha += self.fade_speed
            if self.alpha >= 255:
                self.alpha = 255
                self.state = 'display'

        elif self.state == 'display':
            self.display_timer += 1
            if self.display_timer >= self.display_duration:
                self.state = 'fade_out'

        elif self.state == 'fade_out':
            self.alpha -= self.fade_speed
            if self.alpha <= 0:
                self.alpha = 0
                return True  # Transition complete

        return False  # Transition still in progress

    def draw(self):
        # Create a surface for the transition
        overlay = pygame.Surface((self.width, self.height))
        overlay.fill((0, 0, 0))  # Black background
        overlay.set_alpha(self.alpha)

        # Draw the overlay
        self.screen.blit(overlay, (0, 0))

        # Only draw text when visible enough
        if self.alpha > 70:
            # Render the level text
            text_surface = self.font.render(self.next_level_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(self.width // 2, self.height // 2))

            # Apply alpha to the text
            text_surface.set_alpha(self.alpha)
            self.screen.blit(text_surface, text_rect)

            # Add instruction text
            if self.state == 'display':
                instruction = self.small_font.render("Press any key to continue", True, (200, 200, 200))
                instruction_rect = instruction.get_rect(center=(self.width // 2, self.height // 2 + 50))
                instruction.set_alpha(self.alpha)
                self.screen.blit(instruction, instruction_rect)