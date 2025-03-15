import pgzrun
import random
import math
from pygame import Rect

WIDTH, HEIGHT = 400, 300
TILE_SIZE = 18
WHITE, BLACK = (255, 255, 255), (0, 0, 0)
MENU, PLAYING, GAME_OVER = 0, 1, 2
game_state = MENU

hero_sprites = {'idle': ['heroidle1', 'heroidle2'], 'move': ['heromove1', 'heromove2']}
enemy_sprites = {'idle': ['enemyidle1', 'enemyidle2'], 'move': ['enemymove1', 'enemymove2']}

class Entity:
    def __init__(self, x, y, sprites, speed=2, direction='right'):
        self.x, self.y = x, y
        self.speed = speed
        self.frame = 0
        self.state = 'idle'
        self.direction = direction
        self.hitbox = Rect(self.x, self.y, TILE_SIZE, TILE_SIZE)
        self.sprites = sprites

    def update(self):
        self.frame = (self.frame + 1) % len(self.sprites[self.state])
        self.hitbox.topleft = (self.x, self.y)

    def draw(self):
        sprite = self.sprites[self.state][self.frame] + ('_left' if self.direction == 'left' else '')
        screen.blit(sprite, (self.x, self.y))

class Hero(Entity):
    def __init__(self):
        super().__init__(WIDTH // 2, HEIGHT // 2, hero_sprites, speed=5)
        self.velocity_y = 0
        self.gravity = 0.5
        self.jump_speed = -10
        self.on_ground = False

    def update(self):
        super().update()
        self.velocity_y += self.gravity
        self.y += self.velocity_y
        self.on_ground = False
        for platform in platforms:
            if self.hitbox.colliderect(platform) and self.velocity_y > 0:
                self.y = platform.top - TILE_SIZE
                self.velocity_y = 0
                self.on_ground = True
        if self.y > HEIGHT:
            global game_state
            game_state = GAME_OVER
        if self.y < 0:
            generate_new_game()

    def jump(self):
        if self.on_ground:
            self.velocity_y = self.jump_speed
            sounds.movesound.play()

class Enemy(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, enemy_sprites)
        self.alive = True
        self.angle = 0
        self.amplitude = 20
        self.frequency = 0.05

    def update(self):
        if self.alive:
            super().update()
            self.angle += self.frequency
            self.y += math.sin(self.angle) * self.amplitude * self.frequency
            self.x += self.speed
            if self.x > WIDTH or self.x < 0:
                self.speed *= -1
                self.direction = 'left' if self.speed < 0 else 'right'

def generate_new_game():
    global hero, enemies, platforms
    hero = Hero()
    enemies = [Enemy(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(5)]
    platforms = generate_platforms()

def generate_platforms():
    platforms = [Rect(WIDTH // 2 - TILE_SIZE, HEIGHT // 2 + TILE_SIZE, TILE_SIZE * 2, TILE_SIZE // 2)]
    for i in range(4):
        while True:
            x = random.randint(0, WIDTH - TILE_SIZE * 2)
            y = HEIGHT // 2 - (i + 1) * (TILE_SIZE * 2)
            new_platform = Rect(x, y, TILE_SIZE * 2, TILE_SIZE // 4)
            if not any(new_platform.colliderect(p) for p in platforms):
                platforms.append(new_platform)
                break
    return platforms

def check_enemy_collisions():
    for enemy in enemies:
        if hero.hitbox.colliderect(enemy.hitbox):
            if hero.y + TILE_SIZE < enemy.y + TILE_SIZE // 2:
                enemy.alive = False  # Inimigo é morto
            else:
                global game_state
                game_state = GAME_OVER  # Herói morre

def draw_game_over():
    screen.draw.text("Game Over", center=(WIDTH // 2, HEIGHT // 3), fontsize=60, color=WHITE)
    screen.draw.text("Press R to Restart", center=(WIDTH // 2, HEIGHT // 2), fontsize=40, color=WHITE)
    screen.draw.text("Press Q to Quit", center=(WIDTH // 2, HEIGHT // 2 + 50), fontsize=40, color=WHITE)

def draw_menu():
    screen.draw.text("Platformer Game", center=(WIDTH//2, HEIGHT//4), fontsize=60, color=WHITE)
    screen.draw.text("Start Game", center=(WIDTH//2, HEIGHT//2), fontsize=40, color=WHITE)
    screen.draw.text("Toggle Sounds", center=(WIDTH//2, HEIGHT//2 + 50), fontsize=40, color=WHITE)
    screen.draw.text("Exit", center=(WIDTH//2, HEIGHT//2 + 100), fontsize=40, color=WHITE)

def draw_game():
    for platform in platforms:
        screen.draw.filled_rect(platform, WHITE)
    hero.draw()
    for enemy in enemies:
        if enemy.alive:  # Apenas desenha o inimigo se ele estiver vivo
            enemy.draw()

def update_menu():
    if keyboard.space:
        global game_state
        game_state = PLAYING

def update_game():
    hero.state = 'idle'
    if keyboard.left:
        hero.x -= hero.speed
        hero.state = 'move'
        hero.direction = 'left'
    elif keyboard.right:
        hero.x += hero.speed
        hero.state = 'move'
        hero.direction = 'right'
    if keyboard.up:
        hero.jump()
    hero.update()
    for enemy in enemies:
        enemy.update()
    check_enemy_collisions()

def update():
    global game_state
    if game_state == MENU:
        update_menu()
    elif game_state == PLAYING:
        update_game()
    elif game_state == GAME_OVER:
        if keyboard.r:
            generate_new_game()
            game_state = PLAYING
        elif keyboard.q:
            exit()

def draw():
    screen.fill(BLACK)
    if game_state == MENU:
        draw_menu()
    elif game_state == PLAYING:
        draw_game()
    elif game_state == GAME_OVER:
        draw_game_over()

def on_mouse_down(pos):
    global game_state
    if game_state == MENU:
        if WIDTH//2 - 50 <= pos[0] <= WIDTH//2 + 50 and HEIGHT//2 - 20 <= pos[1] <= HEIGHT//2 + 20:
            game_state = PLAYING
        elif WIDTH//2 - 70 <= pos[0] <= WIDTH//2 + 70 and HEIGHT//2 + 30 <= pos[1] <= HEIGHT//2 + 70:
            toggle_sounds()
        elif WIDTH//2 - 40 <= pos[0] <= WIDTH//2 + 40 and HEIGHT//2 + 80 <= pos[1] <= HEIGHT//2 + 120:
            exit()

def toggle_sounds():
    global sounds_enabled
    sounds_enabled = not sounds_enabled
    sounds.backgroundmusic.set_volume(1.0 if sounds_enabled else 0.0)

hero = Hero()
enemies = [Enemy(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(5)]
platforms = generate_platforms()
sounds.backgroundmusic.play()
sounds_enabled = True

pgzrun.go()
