import pygame
from player import Player

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Katana RPG")
clock = pygame.time.Clock()

player = Player(100, 400)
enemy = pygame.Rect(500, 420, 50, 80)
enemy_alive = True

running = True
while running:
    dt = clock.tick(60)
    screen.fill((30, 30, 30))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    player.handle_input(keys)
    player.update()

    # Перевірка удару
    if enemy_alive and player.attacking:
        hitbox = player.get_attack_hitbox()
        if hitbox and hitbox.colliderect(enemy):
            enemy_alive = False

    player.draw(screen)

    # Малюємо ворога
    if enemy_alive:
        pygame.draw.rect(screen, (50, 200, 50), enemy)

    pygame.display.flip()

pygame.quit()
