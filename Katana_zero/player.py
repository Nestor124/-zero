import pygame
from PIL import Image, ImageSequence

# ======== Player class ========
class Player:
    def __init__(self, x, y, image_path, is_controlled=False):
        self.normal_frames = self.load_gif_frames(image_path, (100, 160))
        self.attack_frames = self.load_gif_frames("aim.d.gif", (180, 200))
        self.frames = self.normal_frames
        self.current_frame = 0
        self.image = self.frames[0]
        self.rect = pygame.Rect(x, y, 100, 160)
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.attacking = False
        self.attack_timer = 0
        self.facing_right = True
        self.is_controlled = is_controlled
        self.frame_delay = 0
        self.attack_started = False
        self.dash_done = False
        self.health = 100  # Для ворога

    def load_gif_frames(self, path, size):
        pil_img = Image.open(path)
        frames = []
        for frame in ImageSequence.Iterator(pil_img):
            frame = frame.convert("RGBA")
            frame = frame.resize(size, Image.Resampling.LANCZOS)
            mode = frame.mode
            data = frame.tobytes()
            py_img = pygame.image.fromstring(data, frame.size, mode)
            frames.append(py_img)
        return frames

    def handle_input(self, keys):
        if self.attacking:
            return

        self.vel_x = 0
        if keys[pygame.K_a]:
            self.vel_x = -5
            self.facing_right = False
        if keys[pygame.K_d]:
            self.vel_x = 5
            self.facing_right = True
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = -20
            self.on_ground = False

        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0] and not self.attacking:
            self.start_attack()

    def start_attack(self):
        self.attacking = True
        self.attack_timer = 0
        self.frames = self.attack_frames
        self.current_frame = 0
        self.frame_delay = 0
        self.attack_started = True
        self.dash_done = False

    def is_attacking(self):
        return self.attacking

    def update(self):
        self.vel_y += 1
        if self.vel_y > 10:
            self.vel_y = 10

        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        # Колізія по землі
        if self.rect.bottom >= 500:
            self.rect.bottom = 500
            self.vel_y = 0
            self.on_ground = True

        # Колізія з баштою по X
        if self.rect.colliderect(tower_rect):
            if self.vel_x > 0:
                self.rect.right = tower_rect.left
            elif self.vel_x < 0:
                self.rect.left = tower_rect.right

        # Колізія з баштою по Y
        if self.rect.colliderect(tower_rect):
            if self.vel_y > 0:
                self.rect.bottom = tower_rect.top
                self.vel_y = 0
                self.on_ground = True
            elif self.vel_y < 0:
                self.rect.top = tower_rect.bottom
                self.vel_y = 0

        if self.attacking:
            self.attack_timer += 1
            if self.current_frame < len(self.frames) - 1:
                self.frame_delay += 1
                if self.frame_delay >= 5:
                    self.current_frame += 1
                    self.image = self.frames[self.current_frame]
                    self.frame_delay = 0

            if self.attack_timer == 60 and not self.dash_done:
                self.rect.x += 200 if self.facing_right else -200
                self.dash_done = True

            if self.attack_timer >= 180:
                self.attacking = False
                self.attack_timer = 0
                self.frames = self.normal_frames
                self.current_frame = 0
                self.image = self.frames[self.current_frame]
        else:
            self.frame_delay += 1
            if self.frame_delay >= 5:
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.image = self.frames[self.current_frame]
                self.frame_delay = 0

    def draw(self, surface, camera_offset_x=0):
        img = self.image
        if not self.facing_right:
            img = pygame.transform.flip(img, True, False)
        surface.blit(img, (self.rect.x - camera_offset_x, self.rect.y))

    def draw_health_bar(self, surface, camera_offset_x):
        bar_width = 100
        bar_height = 10
        health_ratio = self.health / 100
        pygame.draw.rect(surface, (255, 0, 0), (self.rect.x - camera_offset_x, self.rect.y - 20, bar_width, bar_height))
        pygame.draw.rect(surface, (0, 255, 0), (self.rect.x - camera_offset_x, self.rect.y - 20, bar_width * health_ratio, bar_height))

# ======== Ініціалізація гри ========
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 48)

background = pygame.image.load("background.png").convert()
background = pygame.transform.scale(background, screen.get_size())  # масштабування до екрана

tower_rect = pygame.Rect(100, 400, 200, 100)

# ======== Меню ========
def draw_menu():
    screen.fill((30, 30, 30))
    title = font.render("Моя Гра", True, (255, 255, 255))
    start_button = pygame.Rect(300, 300, 200, 60)
    pygame.draw.rect(screen, (70, 130, 180), start_button)
    start_text = font.render("Старт", True, (255, 255, 255))
    screen.blit(title, (320, 150))
    screen.blit(start_text, (start_button.x + 50, start_button.y + 10))
    return start_button

# ======== Стани ========
in_menu = True
pl_zero = Player(150, 300, "pl_zero.gif", is_controlled=True)
pl2_zero = Player(600, 500, "pl2_zero.gif")
camera_offset_x = 0

while True:
    if in_menu:
        start_button = draw_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN and start_button.collidepoint(event.pos):
                in_menu = False
        pygame.display.flip()
        clock.tick(60)
    else:
        # Малюємо фон
        screen.blit(background, (0, 0))

        # Малюємо башту з урахуванням зміщення камери
        pygame.draw.rect(screen, (120, 120, 120), (
            tower_rect.x - camera_offset_x, tower_rect.y,
            tower_rect.width, tower_rect.height
        ))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        keys = pygame.key.get_pressed()
        if pl_zero.is_controlled:
            pl_zero.handle_input(keys)

        pl_zero.update()
        pl2_zero.update()

        # Атака по другому персонажу
        if pl_zero.is_attacking() and pl_zero.rect.colliderect(pl2_zero.rect) and not hasattr(pl2_zero, 'was_hit'):
            pl2_zero.health -= 50
            pl2_zero.was_hit = True
        if not pl_zero.is_attacking() and hasattr(pl2_zero, 'was_hit'):
            del pl2_zero.was_hit

        # Камера
        lock_camera = pl_zero.is_attacking()
        if not lock_camera:
            camera_offset_x = pl_zero.rect.centerx - screen.get_width() // 2

        # Малювання
        pl_zero.draw(screen, camera_offset_x)
        pl2_zero.draw(screen, camera_offset_x)
        pl2_zero.draw_health_bar(screen, camera_offset_x)

        pygame.display.flip()
        clock.tick(60)
