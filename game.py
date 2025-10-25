import pygame
import random
import math
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Killer Bean 9.0")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 0, 200)
YELLOW = (255, 255, 0)
GREY = (50, 50, 50)

# Clock for FPS
clock = pygame.time.Clock()
FPS = 60

# Load assets (simple shapes for demo)
def load_assets():
    # For simplicity, use pygame.Surface with shapes
    player_surf = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.ellipse(player_surf, YELLOW, (0, 0, 40, 40))
    pygame.draw.circle(player_surf, BLACK, (20, 20), 10)
    pygame.draw.rect(player_surf, BLACK, (15, 10, 10, 20))
    
    enemy_surf = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.ellipse(enemy_surf, RED, (0, 0, 40, 40))
    pygame.draw.circle(enemy_surf, BLACK, (20, 20), 10)
    pygame.draw.rect(enemy_surf, BLACK, (15, 10, 10, 20))
    
    bullet_surf = pygame.Surface((10, 4), pygame.SRCALPHA)
    pygame.draw.rect(bullet_surf, BLUE, (0, 0, 10, 4))
    
    return player_surf, enemy_surf, bullet_surf

player_img, enemy_img, bullet_img = load_assets()

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = player_img
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(WIDTH//4, HEIGHT//2))
        self.speed = 5
        self.health = 100
        self.angle = 0
        self.last_shot = 0
        self.shoot_cooldown = 300  # milliseconds

    def update(self, keys, mouse_pos):
        # Movement
        dx = dy = 0
        if keys[pygame.K_w]:
            dy = -self.speed
        if keys[pygame.K_s]:
            dy = self.speed
        if keys[pygame.K_a]:
            dx = -self.speed
        if keys[pygame.K_d]:
            dx = self.speed

        self.rect.x += dx
        self.rect.y += dy

        # Keep inside screen
        self.rect.clamp_ip(screen.get_rect())

        # Rotate towards mouse
        mx, my = mouse_pos
        rel_x, rel_y = mx - self.rect.centerx, my - self.rect.centery
        self.angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def shoot(self, bullets_group):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_cooldown:
            self.last_shot = now
            direction = pygame.math.Vector2(1, 0).rotate(-self.angle)
            bullet = Bullet(self.rect.centerx + direction.x*20, self.rect.centery + direction.y*20, direction)
            bullets_group.add(bullet)

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, speed=2):
        super().__init__()
        self.original_image = enemy_img
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        self.health = 50
        self.angle = 0

    def update(self, player_pos):
        # Move towards player
        px, py = player_pos
        dx, dy = px - self.rect.centerx, py - self.rect.centery
        distance = math.hypot(dx, dy)
        if distance != 0:
            dx, dy = dx / distance, dy / distance
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed

        # Rotate towards player
        self.angle = (180 / math.pi) * -math.atan2(dy, dx)
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = bullet_img
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction
        self.speed = 15
        self.angle = -math.degrees(math.atan2(direction.y, direction.x))
        self.image = pygame.transform.rotate(self.image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def update(self):
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed
        # Remove if off screen
        if not screen.get_rect().colliderect(self.rect):
            self.kill()

# Health bar
def draw_health_bar(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 200
    BAR_HEIGHT = 20
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)

# Game Over screen
def game_over_screen():
    font = pygame.font.SysFont(None, 72)
    text = font.render("GAME OVER", True, RED)
    text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(text, text_rect)
    pygame.display.flip()
    pygame.time.wait(3000)

# Main game function
def main():
    player = Player()
    player_group = pygame.sprite.Group(player)
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()

    spawn_event = pygame.USEREVENT + 1
    pygame.time.set_timer(spawn_event, 1500)

    score = 0
    font = pygame.font.SysFont(None, 36)

    running = True
    while running:
        clock.tick(FPS)
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == spawn_event:
                # Spawn enemy at random edge
                side = random.choice(['top', 'bottom', 'left', 'right'])
                if side == 'top':
                    x = random.randint(0, WIDTH)
                    y = -40
                elif side == 'bottom':
                    x = random.randint(0, WIDTH)
                    y = HEIGHT + 40
                elif side == 'left':
                    x = -40
                    y = random.randint(0, HEIGHT)
                else:
                    x = WIDTH + 40
                    y = random.randint(0, HEIGHT)
                enemy_speed = random.uniform(1.5, 3.0)
                enemy = Enemy(x, y, enemy_speed)
                enemies.add(enemy)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    player.shoot(bullets)

        # Update
        player.update(keys, mouse_pos)
        enemies.update(player.rect.center)
        bullets.update()

        # Bullet hits enemy
        for bullet in bullets:
            hit_enemies = pygame.sprite.spritecollide(bullet, enemies, False)
            for enemy in hit_enemies:
                enemy.health -= 25
                bullet.kill()
                if enemy.health <= 0:
                    enemy.kill()
                    score += 10

        # Enemy hits player
        hit_players = pygame.sprite.spritecollide(player, enemies, False)
        for enemy in hit_players:
            player.health -= 1
            if player.health <= 0:
                running = False

        # Draw
        screen.fill(GREY)
        player_group.draw(screen)
        enemies.draw(screen)
        bullets.draw(screen)
        draw_health_bar(screen, 10, 10, player.health)

        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (WIDTH - 150, 10))

        pygame.display.flip()

    game_over_screen()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
