import pygame
import sys

# Инициализация Pygame
pygame.init()

# Настройки экрана
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Красное Пиво и Голубые Чипсы")

# Цвета 
RED = (255, 0, 0)      # Пиво
BLUE = (0, 0, 255)     # Чипсы
GREEN = (0, 255, 0)    # Платформы
BLACK = (0, 0, 0)      # Фон
WHITE = (255, 255, 255) # Текст
YELLOW = (255, 255, 0)  # Для отладки
PURPLE = (128, 0, 128)  # Выход
LAVA_COLOR = (255, 100, 0)  # Лава (оранжево-красный)
WATER_COLOR = (0, 100, 255)  # Вода (голубой)

# Персонажи
class Character:
    def __init__(self, x, y, color, size=30): #задает характеристики персонажам 
        self.x = x 
        self.y = y
        self.color = color
        self.size = size
        self.speed = 5
        self.jump_power = 12
        self.y_velocity = 0
        self.on_ground = False 
        self.prev_x = x
        self.prev_y = y
        self.start_x = x
        self.start_y = y
    
    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.size, self.size))
    
    def move(self, dx, dy):
        self.prev_x = self.x
        self.prev_y = self.y
        self.x += dx
        self.y += dy
    
    def update(self, platforms, exit_door, hazards):
        # Сохраняем предыдущую позицию
        self.prev_x = self.x
        self.prev_y = self.y
        
        # Гравитация
        self.y_velocity += 0.5
        self.y += self.y_velocity
        
        # Проверка столкновений с платформами
        self.on_ground = False
        
        for platform in platforms:
            # Проверяем столкновение по всем направлениям
            if self.check_collision(platform):
                self.resolve_collision(platform)
          # Проверка столкновений с опасными зонами
        for hazard in hazards:
            if self.check_collision(hazard):
               if (self.color == RED and hazard.type == "water") or \
                   (self.color == BLUE and hazard.type == "lava"):
                    return "dead"  # Огонь гибнет в воде, Вода - в лаве
            else:
                # Может быть другой эффект для "неуязвимости"
                pass
        
        # Проверка достижения выхода
        if self.check_collision(exit_door):
            return "level_complete"
        
        # Границы экрана
        if self.x < 0:
            self.x = 0
        if self.x > WIDTH - self.size:
            self.x = WIDTH - self.size
        if self.y > HEIGHT - self.size:
            self.y = HEIGHT - self.size
            self.y_velocity = 0
            self.on_ground = True
            
     # В классе Character добавляем:
    def die(self):
        # Простая анимация исчезновения
        for i in range(10):
            self.size -= 1
            self.draw()
            pygame.display.flip()
            pygame.time.delay(50)
        
        return None
    
    def check_collision(self, obj):
        return (self.x < obj.x + obj.width and
                self.x + self.size > obj.x and
                self.y < obj.y + obj.height and
                self.y + self.size > obj.y)
    
    def resolve_collision(self, platform):
        # Определяем направление столкновения
        dx = (self.x + self.size/2) - (platform.x + platform.width/2)
        dy = (self.y + self.size/2) - (platform.y + platform.height/2)
        
        # Вычисляем перекрытие по осям
        overlap_x = (self.size/2 + platform.width/2) - abs(dx)
        overlap_y = (self.size/2 + platform.height/2) - abs(dy)
        
        # Определяем направление с наименьшим перекрытием
        if overlap_x < overlap_y:
            if dx > 0:  # Столкновение справа
                self.x = platform.x + platform.width
            else:       # Столкновение слева
                self.x = platform.x - self.size
        else:
            if dy > 0:  # Столкновение снизу
                self.y = platform.y + platform.height
                self.y_velocity = 0
            else:       # Столкновение сверху
                self.y = platform.y - self.size
                self.y_velocity = 0
                self.on_ground = True
    
    def jump(self):
        if self.on_ground:
            self.y_velocity = -self.jump_power
            self.on_ground = False
    
    def reset(self, x, y):
        self.x = x
        self.y = y
        self.y_velocity = 0
        self.on_ground = False

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

# Опасная зона (лава/вода)
class Hazard:
    def __init__(self, x, y, width, height, hazard_type="lava"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = hazard_type
        self.color = LAVA_COLOR if hazard_type == "lava" else WATER_COLOR
    
    def draw(self):
        # Рисуем с небольшим эффектом ряби/пузырьков
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        
        # Добавляем эффект анимации (простой вариант - точки)
        if self.type == "lava":
            # Пузырьки лавы
            for i in range(5):
                bubble_x = self.x + (pygame.time.get_ticks() // 100 + i * 20) % self.width
                bubble_y = self.y + 10 + i * 15
                pygame.draw.circle(screen, YELLOW, (bubble_x, bubble_y), 3)
        else:
            # Волны воды
            for i in range(3):
                wave_x = self.x + (pygame.time.get_ticks() // 50 + i * 40) % self.width
                wave_y = self.y + self.height - 5
                pygame.draw.arc(screen, WHITE, (wave_x, wave_y - 10, 20, 10), 0, 3.14, 2)

# Выход
class ExitDoor:
    def __init__(self, x, y, width=50, height=70):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    
    def draw(self):
        pygame.draw.rect(screen, PURPLE, (self.x, self.y, self.width, self.height))
        # Рисуем дверную ручку
        pygame.draw.circle(screen, YELLOW, (self.x + 35, self.y + self.height//2), 5)

# Уровни
class Level:
    def __init__(self, platforms, exit_door, fire_start, water_start, hazards=None):
        self.platforms = platforms
        self.exit_door = exit_door
        self.fire_start = fire_start
        self.water_start = water_start
        self.hazards = hazards if hazards else []  # Список опасных зон
    
    def draw(self):
        for platform in self.platforms:
            platform.draw()
        for hazard in self.hazards:
            hazard.draw()
        self.exit_door.draw()

# Создание уровней
def create_level_1():
    platforms = [
        Platform(0, 500, 800, 100),  # Земля
        Platform(200, 400, 100, 20),
        Platform(400, 350, 100, 20),
        Platform(600, 300, 100, 20),
        Platform(300, 250, 100, 20),
    ]
    
    hazards = [
        Hazard(350, 520, 100, 80, "lava"),  # Лава в яме
        Hazard(0, 550, 150, 50, "water"),   # Вода слева
    ]
    
    exit_door = ExitDoor(700, 430)
    return Level(platforms, exit_door, (100, 300), (150, 300), hazards)

def create_level_2():
    platforms = [
        Platform(0, 500, 800, 100),  # Земля
        Platform(100, 400, 200, 20),
        Platform(400, 350, 200, 20),
        Platform(100, 250, 200, 20),
        Platform(400, 200, 200, 20),
    ]
    
    hazards = [
        Hazard(300, 500, 100, 100, "lava"),   # Лава между платформами
        Hazard(600, 490, 200, 100, "water"),  # Вода справа
        Hazard(0, 490, 100, 100, "lava"),     # Лава слева
    ]
    
    exit_door = ExitDoor(700, 430)
    return Level(platforms, exit_door, (150, 300), (200, 300), hazards)

def create_level_3():
    platforms = [
        Platform(0, 500, 800, 100),  # Земля
        Platform(150, 400, 50, 20),
        Platform(300, 350, 50, 20),
        Platform(450, 300, 50, 20),
        Platform(600, 250, 50, 20),
        Platform(450, 200, 50, 20),
        Platform(300, 150, 50, 20),
        Platform(150, 100, 50, 20),
        Platform(0, 300, 50, 20),
        Platform(750, 300, 50, 20),
    ]
    exit_door = ExitDoor(375, 30)
    return Level(platforms, exit_door, (50, 300), (100, 300))

# Основная игра
class Game:
    def __init__(self):
        self.levels = [create_level_1(), create_level_2(), create_level_3()]
        self.current_level = 0
        self.fire = Character(*self.levels[self.current_level].fire_start, RED)
        self.water = Character(*self.levels[self.current_level].water_start, BLUE)
        self.font = pygame.font.SysFont(None, 36)
        self.debug_mode = False
        self.game_state = "playing"  # playing, level_complete, game_complete
    
    def load_level(self, level_index):
        if level_index < len(self.levels):
            self.current_level = level_index
            level = self.levels[self.current_level]
            self.fire.reset(*level.fire_start)
            self.water.reset(*level.water_start)
            self.game_state = "playing"
    
    def next_level(self):
        if self.current_level + 1 < len(self.levels):
            self.load_level(self.current_level + 1)
        else:
            self.game_state = "game_complete"
    
    def update(self):
       if self.game_state == "playing":
            # Обновляем персонажей
            fire_result = self.fire.update(self.levels[self.current_level].platforms, 
                                           self.levels[self.current_level].exit_door,
                                           self.levels[self.current_level].hazards)
            water_result = self.water.update(self.levels[self.current_level].platforms, 
                                           self.levels[self.current_level].exit_door,
                                           self.levels[self.current_level].hazards)
        # Проверяем завершение уровня или смерть
            if fire_result == "level_complete" and water_result == "level_complete":
                self.game_state = "level_complete"
            elif fire_result == "dead" or water_result == "dead":
                self.game_state = "dead"
    
    def draw(self):
        # Отрисовка уровня
        self.levels[self.current_level].draw()
    
        # Отрисовка персонажей
        self.fire.draw()
        self.water.draw()
    
        # Отрисовка UI
        level_text = self.font.render(f"Уровень: {self.current_level + 1}/{len(self.levels)}", True, WHITE)
        screen.blit(level_text, (10, 10))
    
        if self.game_state == "level_complete":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            screen.blit(overlay, (0, 0))
            
            complete_text = self.font.render("Уровень пройден!", True, WHITE)
            next_text = self.font.render("Нажмите ПРОБЕЛ для следующего уровня", True, WHITE)
            
            screen.blit(complete_text, (WIDTH//2 - complete_text.get_width()//2, HEIGHT//2 - 50))
            screen.blit(next_text, (WIDTH//2 - next_text.get_width()//2, HEIGHT//2 + 20))
            
        elif self.game_state == "game_complete":
             overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
             overlay.fill((0, 0, 0, 128))
             screen.blit(overlay, (0, 0))
            
             complete_text = self.font.render("Игра пройдена! Поздравляем!", True, WHITE)
             restart_text = self.font.render("Нажмите Q для перезапуска", True, WHITE)
            
             screen.blit(complete_text, (WIDTH//2 - complete_text.get_width()//2, HEIGHT//2 - 50))
             screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 20))
             
        elif self.game_state == "dead":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 0, 0, 64))  # Красный полупрозрачный overlay
            screen.blit(overlay, (0, 0))
        
            dead_text = self.font.render("Персонаж погиб!", True, WHITE)
            restart_text = self.font.render("Нажмите R для перезапуска уровня", True, WHITE)
        
            screen.blit(dead_text, (WIDTH//2 - dead_text.get_width()//2, HEIGHT//2 - 50))
            screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 20))

# Создание игры
game = Game()
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w and game.game_state == "playing":
                game.fire.jump()
            if event.key == pygame.K_UP and game.game_state == "playing":
                game.water.jump()
            if event.key == pygame.K_F1:
                game.debug_mode = not game.debug_mode
            if event.key == pygame.K_SPACE and game.game_state == "level_complete":
                game.next_level()
            if event.key == pygame.K_r:
                game.load_level(game.current_level)  # Перезагружаем текущий уровень
            if event.key == pygame.K_q and game.game_state == "game_complete":
                game.load_level(0)
    

    # Управление
    if game.game_state == "playing":
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            game.fire.move(-game.fire.speed, 0)
        if keys[pygame.K_d]:
            game.fire.move(game.fire.speed, 0)
        if keys[pygame.K_LEFT]:
            game.water.move(-game.water.speed, 0)
        if keys[pygame.K_RIGHT]:
            game.water.move(game.water.speed, 0)
        
    # Обновление игры
    game.update()
    
    # Отрисовка
    screen.fill(BLACK)
    game.draw()
    
    # Обновление экрана
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
