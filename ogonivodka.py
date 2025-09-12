import pygame
import sys

# Инициализация Pygame
pygame.init()

# Настройки экрана
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Огонь и Вода")

# Цвета
RED = (255, 0, 0)      # Огонь
BLUE = (0, 0, 255)     # Вода
GREEN = (0, 255, 0)    # Платформы
BLACK = (0, 0, 0)      # Фон
WHITE = (255, 255, 255) # Текст

# Персонажи
class Character:
    def __init__(self, x, y, color, size=30):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.speed = 5
        self.jump_power = 10
        self.y_velocity = 0
        self.on_ground = False
    
    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.size, self.size))
    
    def move(self, dx, dy):
        self.x += dx
        self.y += dy
    
    def update(self, platforms):
        # Гравитация
        self.y_velocity += 0.5
        self.y += self.y_velocity
        
        # Проверка столкновений с платформами
        self.on_ground = False
        for platform in platforms:
            if (self.y + self.size >= platform.y and 
                self.y + self.size <= platform.y + 10 and
                self.x + self.size > platform.x and 
                self.x < platform.x + platform.width and
                self.y_velocity > 0):
                self.y = platform.y - self.size
                self.y_velocity = 0
                self.on_ground = True

            elif (self.y <= platform.y + platform.height and 
                self.y + self.size > platform.y + platform.height and
                self.x + self.size > platform.x and 
                self.x < platform.x + platform.width and
                self.y_velocity < 0):  # Только если движется вверх
                self.y = platform.y + platform.height
                self.y_velocity = 0

            #elif (self.x <= platform.x + platform.width and
                  #self.x + self.size > platform.x + platform.width and
                  #self.y + self.size > platform.y + platform.height and
                  #self.x < platform.x + platform.width):
                #if (self.y_velocity <0 or self.y_velocity >0):
                  #self.y = platform.y + platform.height
                  #self.x = self.x
                  #self.y_velocity = 0
        
        # Границы экрана
        if self.x < 0:
            self.x = 0
        if self.x > WIDTH - self.size:
            self.x = WIDTH - self.size
        if self.y > HEIGHT - self.size:
            self.y = HEIGHT - self.size
            self.y_velocity = 0
            self.on_ground = True
    
    def jump(self):
        if self.on_ground:
            self.y_velocity = -self.jump_power

# Платформы
class Platform:
    def __init__(self, x, y, width, height, color=GREEN):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
    
    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

# Создание персонажей
fire = Character(100, 300, RED)
water = Character(150, 300, BLUE)

# Создание платформ
platforms = [
    Platform(0, 500, 800, 100),  # Земля
    Platform(200, 400, 100, 20),  # Платформа 1
    Platform(400, 350, 100, 20),  # Платформа 2
    Platform(600, 300, 100, 20),  # Платформа 3
]

# Игровой цикл
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                fire.jump()
            if event.key == pygame.K_UP:
                water.jump()
    
    # Управление огнем (WASD)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        fire.move(-fire.speed, 0)
    if keys[pygame.K_d]:
        fire.move(fire.speed, 0)
    
    # Управление водой (Стрелки)
    if keys[pygame.K_LEFT]:
        water.move(-water.speed, 0)
    if keys[pygame.K_RIGHT]:
        water.move(water.speed, 0)
    
    # Обновление персонажей
    fire.update(platforms)
    water.update(platforms)
    
    # Отрисовка
    screen.fill(BLACK)
    
    # Рисуем платформы
    for platform in platforms:
        platform.draw()
    
    # Рисуем персонажей
    fire.draw()
    water.draw()
    
    # Обновление экрана
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
