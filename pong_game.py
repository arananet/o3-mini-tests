"""
Pong Game – Player vs Computer
--------------------------------

Controls:
  • Up / Down Arrow keys – move the player’s paddle.
  
Goal:
  The player competes against the computer. Each side starts with 3 lives.
  When the ball goes past a paddle, that side loses one life.
  Keep track of the score and lives.
  
Required assets (optional):
  • player.png      → sprite for the player paddle.
  • computer.png    → sprite for the computer paddle.
  • ball.png        → sprite for the ball.

If the image files are not present, the game will display simple shapes.
  
Make sure pygame is installed (pip install pygame).
Run with: python pong_game.py
"""

import pygame, sys, os, random

pygame.init()

# --------------
# Constants & Settings
# --------------
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60

PADDLE_WIDTH, PADDLE_HEIGHT = 20, 100
BALL_SIZE = 20

PLAYER_SPEED = 7
# Computer paddle speed. (The computer will “track” the ball but, if you wish, you can add slight delay.)
COMP_SPEED = 6

STARTING_LIVES = 3

# Colors (for fallback drawing)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE  = (50, 100, 255)
RED   = (255, 50, 50)

# --------------
# Initialize display and clock
# --------------
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pong – Player vs Computer")
clock = pygame.time.Clock()

# --------------
# Font for HUD (score & lives)
# --------------
font = pygame.font.SysFont(None, 36)

# --------------
# Helper function to load an image with fallback.
# --------------
def load_sprite(image_name, fallback_size, fill_color):
    fullpath = os.path.join(os.path.dirname(__file__), image_name)
    try:
        image = pygame.image.load(fullpath)
        image = image.convert_alpha()
    except Exception as e:
        # If image loading fails, return a Surface filled with color.
        image = pygame.Surface(fallback_size)
        image.fill(fill_color)
    return image

# --------------
# Paddle Sprite Class
# --------------
class Paddle(pygame.sprite.Sprite):
    def __init__(self, x, y, is_player=True):
        super().__init__()
        self.is_player = is_player
        # Use different images for player and computer.
        if self.is_player:
            self.image = load_sprite("player.png", (PADDLE_WIDTH, PADDLE_HEIGHT), BLUE)
        else:
            self.image = load_sprite("computer.png", (PADDLE_WIDTH, PADDLE_HEIGHT), RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
    def update(self, dy):
        self.rect.y += dy
        # Keep paddle within vertical boundaries.
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

# --------------
# Ball Sprite Class
# --------------
class Ball(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_sprite("ball.png", (BALL_SIZE, BALL_SIZE), WHITE)
        self.rect = self.image.get_rect()
        self.reset()
    
    def reset(self):
        # Place ball in center.
        self.rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
        # Randomize initial direction.
        dir_x = random.choice([-1, 1])
        dir_y = random.choice([-1, 1])
        self.speed_x = 7 * dir_x
        self.speed_y = 7 * dir_y
        
    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        
        # Bounce off top and bottom.
        if self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.speed_y *= -1

# --------------
# Create sprite groups
# --------------
all_sprites = pygame.sprite.Group()
paddle_group = pygame.sprite.Group()

# Create player paddle – placed at left side.
player_paddle = Paddle(30, SCREEN_HEIGHT//2 - PADDLE_HEIGHT//2, is_player=True)
paddle_group.add(player_paddle)
all_sprites.add(player_paddle)

# Create computer paddle – placed at right side.
comp_paddle = Paddle(SCREEN_WIDTH - 30 - PADDLE_WIDTH, SCREEN_HEIGHT//2 - PADDLE_HEIGHT//2, is_player=False)
paddle_group.add(comp_paddle)
all_sprites.add(comp_paddle)

# Create ball.
ball = Ball()
all_sprites.add(ball)

# --------------
# Game Variables (score & lives)
# --------------
player_score = 0
player_lives = STARTING_LIVES
comp_score = 0
comp_lives = STARTING_LIVES

# --------------
# Main Game Loop
# --------------
running = True
while running:
    clock.tick(FPS)
    
    # --- Event Processing ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # --- Player Input (Up/Down keys) ---
    keys = pygame.key.get_pressed()
    dy = 0
    if keys[pygame.K_UP]:
        dy = -PLAYER_SPEED
    if keys[pygame.K_DOWN]:
        dy = PLAYER_SPEED
    player_paddle.update(dy)
    
    # --- Computer Paddle AI ---
    # A simple strategy: move the computer paddle toward the ball.
    if ball.rect.centery < comp_paddle.rect.centery:
        comp_paddle.update(-COMP_SPEED)
    elif ball.rect.centery > comp_paddle.rect.centery:
        comp_paddle.update(COMP_SPEED)
    
    # --- Update Ball Position ---
    ball.update()
    
    # --- Check for Collisions with Paddles ---
    # If the ball hits the paddles, reverse its horizontal direction.
    if ball.rect.colliderect(player_paddle.rect) and ball.speed_x < 0:
        ball.speed_x *= -1
        # Optionally add a slight random variation for challenge.
        ball.speed_y += random.choice([-1, 1])
        
    if ball.rect.colliderect(comp_paddle.rect) and ball.speed_x > 0:
        ball.speed_x *= -1
        ball.speed_y += random.choice([-1, 1])
    
    # --- Check if Ball Went Off-Screen ---
    # If the ball leaves the left side, the player loses a life and computer gains a point.
    if ball.rect.right < 0:
        comp_score += 1
        player_lives -= 1
        ball.reset()
        
    # If the ball leaves the right side, the computer loses a life and the player gains a point.
    if ball.rect.left > SCREEN_WIDTH:
        player_score += 1
        comp_lives -= 1
        ball.reset()
    
    # --- Check for Game Over ---
    if player_lives <= 0 or comp_lives <= 0:
        running = False  # End the game loop.
    
    # --- Drawing ---
    screen.fill(BLACK)
    
    # Draw all sprites.
    all_sprites.draw(screen)
    
    # Draw HUD (Score and Lives) at the top.
    hud_text = f"Player: {player_score}   Lives: {player_lives}    |    Computer: {comp_score}   Lives: {comp_lives}"
    hud_surface = font.render(hud_text, True, WHITE)
    screen.blit(hud_surface, (20, 20))
    
    pygame.display.flip()

# --- Game Over Screen ---
screen.fill(BLACK)
if player_lives <= 0:
    over_text = "Game Over! You lost!"
else:
    over_text = "Congratulations! You won!"
msg_surface = font.render(over_text, True, WHITE)
prompt_surface = font.render("Press any key to exit.", True, WHITE)
screen.blit(msg_surface, (SCREEN_WIDTH//2 - msg_surface.get_width()//2, SCREEN_HEIGHT//2 - 40))
screen.blit(prompt_surface, (SCREEN_WIDTH//2 - prompt_surface.get_width()//2, SCREEN_HEIGHT//2 + 10))
pygame.display.flip()

# Wait for a key press before quitting.
waiting = True
while waiting:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            waiting = False
        if event.type == pygame.KEYDOWN:
            waiting = False

pygame.quit()
sys.exit()
