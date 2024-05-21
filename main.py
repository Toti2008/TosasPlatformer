import pygame
import sys
import random
import math



# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 50
PLAYER_COLOR = (255, 0, 0)
PLATFORM_COLOR = (0, 255, 0)
SWORD_COLOR = (255, 255, 0)
GRAVITY = 1
JUMP_STRENGTH = 15
MOVE_SPEED = 5
MAX_FALL_SPEED = 20
GROUND_LEVEL = SCREEN_HEIGHT - PLAYER_HEIGHT
SWORD_DAMAGE = 10
SWORD_RANGE = 100  # Define SWORD_RANGE here
ENEMY_WIDTH = 50
ENEMY_HEIGHT = 50
ENEMY_COLOR = (0, 0, 255)
ENEMY_SPEED = 2

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tosas Platformer Demo")

# Button class
class Button:
    def __init__(self, x, y, width, height, color, text, text_color, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.text_surface = pygame.font.Font(None, 36).render(text, True, text_color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)
        self.action = action

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        screen.blit(self.text_surface, self.text_rect)

    def clicked(self):
        if self.action:
            self.action()

# Particle class
class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.Surface((2, 2))  # Smaller particle size
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 5)
        self.velocity_x = math.cos(angle) * speed
        self.velocity_y = math.sin(angle) * speed
        self.lifetime = 20

    def update(self):
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
        self.image.fill(PLAYER_COLOR)
        self.original_image = self.image.copy()
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH // 2
        self.rect.y = SCREEN_HEIGHT // 2
        self.velocity_y = 0
        self.on_ground = False
        self.double_jump = False
        self.rotation = 0
        self.sword_swinging = False
        self.sword_angle = 0
        self.health = 100

    def update(self):
        # Apply gravity
        self.velocity_y += GRAVITY
        if self.velocity_y > MAX_FALL_SPEED:
            self.velocity_y = MAX_FALL_SPEED

        # Move the player vertically
        self.rect.y += self.velocity_y

        # Check for ground collision
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.on_ground = True
            self.double_jump = False
            self.rotation = 0  # Reset rotation when on the ground
            self.image = self.original_image  # Reset image when on the ground
        else:
            self.on_ground = False

        # Screen wrapping
        if self.rect.left > SCREEN_WIDTH:
            self.rect.right = 0
        elif self.rect.right < 0:
            self.rect.left = SCREEN_WIDTH

        # Check for collisions with platforms
        if pygame.sprite.spritecollideany(self, platforms):
            if self.velocity_y > 0:  # Only reset when falling down
                self.on_ground = True
                self.rect.y -= self.velocity_y  # Move the player back to previous position
                self.rotation = 0  # Reset rotation
                self.image = self.original_image  # Reset image when on the platform

        # Handle sword swinging
        if self.sword_swinging:
            self.sword_angle += 15
            if self.sword_angle >= 180:
                self.sword_swinging = False
                self.sword_angle = 0
            create_sword_particles(self.rect.centerx, self.rect.centery)

    

    def jump(self):
        if self.on_ground or (not self.on_ground and not self.double_jump):
            self.velocity_y = -JUMP_STRENGTH
            
            if not self.on_ground:
                self.double_jump = True
            self.on_ground = False
            self.rotation = 0  # Reset rotation when starting a jump
            create_particles(self.rect.centerx, self.rect.bottom, (255, 255, 255))  # Create jump particles

    def apply_rotation(self):
        if not self.on_ground:
            self.rotation += 10  # Increase the rotation angle
            self.image = pygame.transform.rotate(self.original_image, self.rotation)
            self.rect = self.image.get_rect(center=self.rect.center)

    def swing_sword(self):
        if not self.sword_swinging:
            self.sword_swinging = True
            self.sword_angle = 0
            


            
    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            pygame.quit()
            sys.exit()

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT))
        self.image.fill(ENEMY_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.velocity_x = ENEMY_SPEED

    def update(self):
        self.rect.x += self.velocity_x

        # Check for screen collision
        if self.rect.right > SCREEN_WIDTH:
            self.velocity_x = -ENEMY_SPEED
        elif self.rect.left < 0:
            self.velocity_x = ENEMY_SPEED

        # Check for collisions with player
        if pygame.sprite.collide_rect(self, player):
            if player.sword_swinging:
                self.kill()
            else:
                player.take_damage(10)



# Platform class
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(PLATFORM_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Create the player
player = Player()

# Create platforms
platforms = pygame.sprite.Group()
platform = Platform(200, 500, 400, 20)
platforms.add(platform)

# Group all sprites
all_sprites = pygame.sprite.Group()
all_sprites.add(player)
all_sprites.add(platform)



# Group particles
particles = pygame.sprite.Group()

# Create particles function
def create_particles(x, y, color):
    for _ in range(20):
        particle = Particle(x, y, color)
        particles.add(particle)
        all_sprites.add(particle)

# Create sword particles function
def create_sword_particles(x, y):
    for _ in range(5):
        particle = Particle(x, y, SWORD_COLOR)
        particles.add(particle)
        all_sprites.add(particle)

# Main menu function
def main_menu():
    play_button = Button(300, 300, 200, 50, (0, 255, 0), "Play", (0, 0, 0), start_game)
    quit_button = Button(300, 400, 200, 50, (255, 0, 0), "Quit", (0, 0, 0), quit_game)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    if play_button.rect.collidepoint(event.pos):
                        play_button.clicked()
                    elif quit_button.rect.collidepoint(event.pos):
                        quit_button.clicked()

        screen.fill((0, 0, 0))
        title_text = pygame.font.Font(None, 48).render("Tosas Platformer", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        screen.blit(title_text, title_rect)

        play_button.draw()
        quit_button.draw()

        pygame.display.flip()

# Start game function
def start_game():
    # Game loop
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    player.jump()
                elif event.key == pygame.K_x:
                    player.swing_sword()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.rect.x -= MOVE_SPEED
        if keys[pygame.K_RIGHT]:
            player.rect.x += MOVE_SPEED

        # Update all sprites
        all_sprites.update()
        player.apply_rotation()  # Apply rotation to the player sprite

        # Create landing particles if the player lands
        if player.on_ground and player.velocity_y == 0:
            create_particles(player.rect.centerx, player.rect.bottom, (255, 255, 255))

        # Draw everything
        screen.fill((0, 0, 0))  # Fill the screen with black
        all_sprites.draw(screen)

        # Draw sword if swinging
        if player.sword_swinging:
            angle_rad = math.radians(player.sword_angle)
            sword_length = 50
            start_pos = (player.rect.centerx, player.rect.centery)
            end_pos = (
                player.rect.centerx + sword_length * math.cos(angle_rad),
                player.rect.centery + sword_length * math.sin(angle_rad)
            )
            pygame.draw.line(screen, SWORD_COLOR, start_pos, end_pos, 5)

        
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(60)

# Quit game function
def quit_game():
    pygame.quit()
    sys.exit()

# Run the main menu
if __name__ == "__main__":
    main_menu()

