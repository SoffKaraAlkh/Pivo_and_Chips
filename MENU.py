import pygame
import sys

# Инициализация Pygame
pygame.init()

# Настройки экрана
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Красное Пиво и Голубые Чипсы")

# Состояния игры
MENU = "menu"
PLAYING = "playing"
LEVEL_COMPLETE = "level_complete"
GAME_COMPLETE = "game_complete"
DEAD = "dead"
SETTINGS = "settings"

# Цвета
BUTTON_COLOR = (70, 130, 180)
BUTTON_HOVER_COLOR = (100, 160, 210)
TITLE_COLOR = (255, 215, 0)  # Золотой
RED = (255, 0, 0)      # Пиво
BLUE = (0, 0, 255)     # Чипсы
GREEN = (0, 255, 0)    # Платформы
BLACK = (0, 0, 0)      # Фон
WHITE = (255, 255, 255) # Текст
YELLOW = (255, 255, 0)  # Для отладки
PURPLE = (128, 0, 128)  # Выход
LAVA_COLOR = (255, 100, 0)  # Лава (оранжево-красный)
WATER_COLOR = (0, 100, 255)  # Вода (голубой)


class ScalingSystem:
    def __init__(self, base_width=800, base_height=600):
        self.base_width = base_width
        self.base_height = base_height
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.offset_x = 0
        self.offset_y = 0
    
    def update_scale(self, current_width, current_height):
        """Обновляет коэффициенты масштабирования"""
        self.scale_x = current_width / self.base_width
        self.scale_y = current_height / self.base_height
        
        # Сохраняем пропорции (можно убрать, если нужно растягивать)
        scale = min(self.scale_x, self.scale_y)
        self.scale_x = scale
        self.scale_y = scale
        
        # Центрируем изображение
        self.offset_x = (current_width - self.base_width * scale) / 2
        self.offset_y = (current_height - self.base_height * scale) / 2
    
    def scale_position(self, x, y):
        """Масштабирует позицию"""
        return (x * self.scale_x + self.offset_x, y * self.scale_y + self.offset_y)
    
    def scale_size(self, width, height):
        """Масштабирует размеры"""
        return (width * self.scale_x, height * self.scale_y)
    
    def inverse_scale_position(self, x, y):
        """Обратное масштабирование позиции (для мыши)"""
        return ((x - self.offset_x) / self.scale_x, (y - self.offset_y) / self.scale_y)




class Button:
    def __init__(self, x, y, width, height, text, color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR):
        self.base_x = x
        self.base_y = y
        self.base_width = width
        self.base_height = height
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.font = pygame.font.SysFont(None, 36)
        self.is_hovered = False
        self.rect = pygame.Rect(x, y, width, height)
    
    def update_rect(self, scaling_system):
        """Обновляет прямоугольник кнопки с учетом масштабирования"""
        scaled_x, scaled_y = scaling_system.scale_position(self.base_x, self.base_y)
        scaled_width, scaled_height = scaling_system.scale_size(self.base_width, self.base_height)
        self.rect = pygame.Rect(scaled_x, scaled_y, scaled_width, scaled_height)
    
    def draw(self, screen, scaling_system):
        # Обновляем прямоугольник перед отрисовкой
        self.update_rect(scaling_system)
        
        # Рисуем кнопку
        pygame.draw.rect(screen, self.current_color, self.rect, border_radius=int(10 * scaling_system.scale_x))
        pygame.draw.rect(screen, WHITE, self.rect, int(2 * scaling_system.scale_x), border_radius=int(10 * scaling_system.scale_x))
        
        # Масштабируем шрифт
        font_size = int(36 * scaling_system.scale_x)
        font = pygame.font.SysFont(None, font_size)
        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def check_hover(self, pos, scaling_system):
        self.update_rect(scaling_system)
        self.is_hovered = self.rect.collidepoint(pos)
        self.current_color = self.hover_color if self.is_hovered else self.color
        return self.is_hovered
    
    def is_clicked(self, pos, event, scaling_system):
        self.update_rect(scaling_system)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

class Menu:
    def __init__(self, scaling_system):
        self.buttons = []
        self.scaling_system = scaling_system
        self.title_font_size = 72
        self.create_main_menu()
    
    def create_main_menu(self):
        center_x = self.scaling_system.base_width // 2
        self.buttons = [
            Button(center_x - 100, 200, 200, 50, "Играть"),
            Button(center_x - 100, 270, 200, 50, "Настройки"),
            Button(center_x - 100, 340, 200, 50, "Выйти")
        ]
    
    def create_settings_menu(self):
        center_x = self.scaling_system.base_width // 2
        self.buttons = [
            Button(center_x - 150, 200, 300, 50, "Оконный режим"),
            Button(center_x - 150, 270, 300, 50, "Полноэкранный режим"),
            Button(center_x - 100, 340, 200, 50, "Назад")
        ]
    
    def draw(self, screen, game_state):
        # Фон меню
        screen.fill((30, 30, 60))
        
        # Заголовок (масштабированный)
        title_font_size = int(self.title_font_size * self.scaling_system.scale_x)
        title_font = pygame.font.SysFont(None, title_font_size)
        title_text = "Красное Пиво и Голубые Чипсы"
        title_surface = title_font.render(title_text, True, TITLE_COLOR)
        title_rect = title_surface.get_rect(center=(WIDTH//2, 100 * self.scaling_system.scale_y + self.scaling_system.offset_y))
        screen.blit(title_surface, title_rect)
        
        # Подзаголовок для настроек
        if game_state == SETTINGS:
            subtitle_font_size = int(48 * self.scaling_system.scale_x)
            subtitle_font = pygame.font.SysFont(None, subtitle_font_size)
            settings_text = "Настройки"
            settings_surface = subtitle_font.render(settings_text, True, WHITE)
            settings_rect = settings_surface.get_rect(center=(WIDTH//2, 150 * self.scaling_system.scale_y + self.scaling_system.offset_y))
            screen.blit(settings_surface, settings_rect)
        
        # Кнопки
        for button in self.buttons:
            button.draw(screen, self.scaling_system)
    
    def handle_event(self, event, game):
        mouse_pos = pygame.mouse.get_pos()
        
        for button in self.buttons:
            button.check_hover(mouse_pos, self.scaling_system)
            
            if button.is_clicked(mouse_pos, event, self.scaling_system):
                if game.game_state == MENU:
                    if button.text == "Играть":
                        game.game_state = PLAYING
                        game.load_level(0)
                    elif button.text == "Настройки":
                        self.create_settings_menu()
                        game.game_state = SETTINGS
                    elif button.text == "Выйти":
                        return "quit"
                
                elif game.game_state == SETTINGS:
                    if button.text == "Оконный режим":
                        game.set_windowed()
                    elif button.text == "Полноэкранный режим":
                        game.set_fullscreen()
                    elif button.text == "Назад":
                        self.create_main_menu()
                        game.game_state = MENU
        
        return "continue"
# Персонажи
class Character:
    def __init__(self, x, y, color, size=30):
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
    
    def draw(self, scaling_system):
        scaled_x, scaled_y = scaling_system.scale_position(self.x, self.y)
        scaled_size_x, scaled_size_y = scaling_system.scale_size(self.size, self.size)
        pygame.draw.rect(screen, self.color, (scaled_x, scaled_y, scaled_size_x, scaled_size_y))
    
    def get_scaled_rect(self, scaling_system):
        """Возвращает масштабированный прямоугольник для столкновений"""
        scaled_x, scaled_y = scaling_system.scale_position(self.x, self.y)
        scaled_size_x, scaled_size_y = scaling_system.scale_size(self.size, self.size)
        return pygame.Rect(scaled_x, scaled_y, scaled_size_x, scaled_size_y)
    
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
    
    def draw(self, scaling_system):
        scaled_x, scaled_y = scaling_system.scale_position(self.x, self.y)
        scaled_width, scaled_height = scaling_system.scale_size(self.width, self.height)
        pygame.draw.rect(screen, self.color, (scaled_x, scaled_y, scaled_width, scaled_height))

# Опасная зона (лава/вода)
class Hazard:
    def __init__(self, x, y, width, height, hazard_type="lava"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = hazard_type
        self.color = LAVA_COLOR if hazard_type == "lava" else WATER_COLOR
    
    def draw(self, scaling_system):
        scaled_x, scaled_y = scaling_system.scale_position(self.x, self.y)
        scaled_width, scaled_height = scaling_system.scale_size(self.width, self.height)
        
        # Основной прямоугольник
        pygame.draw.rect(screen, self.color, (scaled_x, scaled_y, scaled_width, scaled_height))
        
        # Добавляем эффект анимации (простой вариант - точки)
        if self.type == "lava":
            for i in range(5):
                bubble_x = self.x + (pygame.time.get_ticks() // 100 + i * 20) % self.width
                bubble_y = self.y + 10 + i * 15
                scaled_bubble_x, scaled_bubble_y = scaling_system.scale_position(bubble_x, bubble_y)
                bubble_size = max(2, 3 * scaling_system.scale_x)  # Минимальный размер
                pygame.draw.circle(screen, YELLOW, (scaled_bubble_x, scaled_bubble_y), bubble_size)
        else:
            # Волны воды
            for i in range(3):
                wave_offset = (pygame.time.get_ticks() // 50 + i * 40) % self.width
                wave_x = self.x + wave_offset
                wave_y = self.y + self.height - 5
                
                scaled_wave_x, scaled_wave_y = scaling_system.scale_position(wave_x, wave_y)
                wave_width = 20 * scaling_system.scale_x
                wave_height = 10 * scaling_system.scale_y
                
                # Рисуем волну как дугу
                wave_rect = (scaled_wave_x, scaled_wave_y - wave_height, wave_width, wave_height)
                pygame.draw.arc(screen, WHITE, wave_rect, 0, 3.14, int(2 * scaling_system.scale_x))
            

# Выход
class ExitDoor:
    def __init__(self, x, y, width=50, height=70):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    
    def draw(self, scaling_system):
        scaled_x, scaled_y = scaling_system.scale_position(self.x, self.y)
        scaled_width, scaled_height = scaling_system.scale_size(self.width, self.height)
        
        # Дверь
        pygame.draw.rect(screen, PURPLE, (scaled_x, scaled_y, scaled_width, scaled_height))
        
        # Ручка (масштабированная)
        handle_x, handle_y = scaling_system.scale_position(self.x + 35, self.y + self.height//2)
        handle_size = max(3, 5 * scaling_system.scale_x)
        pygame.draw.circle(screen, YELLOW, (handle_x, handle_y), handle_size)

# Уровни
class Level:
    def __init__(self, platforms, exit_door, fire_start, water_start, hazards=None):
        self.platforms = platforms
        self.exit_door = exit_door
        self.fire_start = fire_start
        self.water_start = water_start
        self.hazards = hazards if hazards else []
    
    def draw(self, scaling_system):
        for platform in self.platforms:
            platform.draw(scaling_system)
        for hazard in self.hazards:
            hazard.draw(scaling_system)
        self.exit_door.draw(scaling_system)

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
        self.game_state = MENU
        self.scaling_system = ScalingSystem()  # Добавляем систему масштабирования
        self.menu = Menu(self.scaling_system)  # Передаем систему масштабирования в меню
        self.fullscreen = False
        # Обновляем масштабирование при инициализации
        self.scaling_system.update_scale(WIDTH, HEIGHT)

    def load_level(self, level_index):
        """Загружает уровень по индексу"""
        if level_index < len(self.levels):
            self.current_level = level_index
            level = self.levels[self.current_level]
            self.fire.reset(*level.fire_start)
            self.water.reset(*level.water_start)
            self.game_state = PLAYING

    def next_level(self):
        """Переходит на следующий уровень"""
        if self.current_level + 1 < len(self.levels):
            self.load_level(self.current_level + 1)
        else:
            self.game_state = GAME_COMPLETE
    
    def set_fullscreen(self):
        global screen, WIDTH, HEIGHT
        self.fullscreen = True
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        WIDTH, HEIGHT = screen.get_size()
        self.scaling_system.update_scale(WIDTH, HEIGHT)  # Обновляем масштабирование
        if hasattr(self, 'menu'):
            self.menu.create_settings_menu()
    
    def set_windowed(self):
        global screen, WIDTH, HEIGHT
        self.fullscreen = False
        WIDTH, HEIGHT = 800, 600
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.scaling_system.update_scale(WIDTH, HEIGHT)  # Обновляем масштабирование
        if hasattr(self, 'menu'):
            self.menu.create_settings_menu()
    
    def update(self):
        if self.game_state == PLAYING:
            fire_result = self.fire.update(self.levels[self.current_level].platforms, 
                                         self.levels[self.current_level].exit_door,
                                         self.levels[self.current_level].hazards)
            water_result = self.water.update(self.levels[self.current_level].platforms, 
                                           self.levels[self.current_level].exit_door,
                                           self.levels[self.current_level].hazards)
            
            if fire_result == "level_complete" and water_result == "level_complete":
                self.game_state = LEVEL_COMPLETE
            elif fire_result == "dead" or water_result == "dead":
                self.game_state = DEAD
    
    def draw(self):
        # Всегда обновляем масштабирование перед отрисовкой
        self.scaling_system.update_scale(WIDTH, HEIGHT)
        
        if self.game_state in [PLAYING, LEVEL_COMPLETE, DEAD, GAME_COMPLETE]:
            # Отрисовка игрового уровня с масштабированием
            self.levels[self.current_level].draw(self.scaling_system)
            self.fire.draw(self.scaling_system)
            self.water.draw(self.scaling_system)
            
            # UI элементы (масштабированные)
            font_size = int(36 * self.scaling_system.scale_x)
            font = pygame.font.SysFont(None, font_size)
            level_text = font.render(f"Уровень: {self.current_level + 1}/{len(self.levels)}", True, WHITE)
            text_x = 10 * self.scaling_system.scale_x + self.scaling_system.offset_x
            text_y = 10 * self.scaling_system.scale_y + self.scaling_system.offset_y
            screen.blit(level_text, (text_x, text_y))
            
            # Сообщения о завершении уровня/смерти
            if self.game_state == LEVEL_COMPLETE:
                self.draw_level_complete()
            elif self.game_state == DEAD:
                self.draw_dead_screen()
            elif self.game_state == GAME_COMPLETE:
                self.draw_game_complete()
        
        elif self.game_state in [MENU, SETTINGS]:
            # Отрисовка меню
            self.menu.draw(screen, self.game_state)
    
    def draw_level_complete(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        font_size = int(36 * self.scaling_system.scale_x)
        font = pygame.font.SysFont(None, font_size)
        
        complete_text = font.render("Уровень пройден!", True, WHITE)
        next_text = font.render("Нажмите ПРОБЕЛ для следующего уровня", True, WHITE)
        menu_text = font.render("Нажмите M для выхода в меню", True, WHITE)
        
        center_x = WIDTH // 2
        center_y = HEIGHT // 2
        
        screen.blit(complete_text, (center_x - complete_text.get_width()//2, center_y - 50))
        screen.blit(next_text, (center_x - next_text.get_width()//2, center_y + 20))
        screen.blit(menu_text, (center_x - menu_text.get_width()//2, center_y + 60))
    
    def draw_dead_screen(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 0, 0, 64))
        screen.blit(overlay, (0, 0))
        
        font_size = int(36 * self.scaling_system.scale_x)
        font = pygame.font.SysFont(None, font_size)
        
        dead_text = font.render("Персонаж погиб!", True, WHITE)
        restart_text = font.render("Нажмите R для перезапуска уровня", True, WHITE)
        menu_text = font.render("Нажмите M для выхода в меню", True, WHITE)
        
        center_x = WIDTH // 2
        center_y = HEIGHT // 2
        
        screen.blit(dead_text, (center_x - dead_text.get_width()//2, center_y - 50))
        screen.blit(restart_text, (center_x - restart_text.get_width()//2, center_y + 20))
        screen.blit(menu_text, (center_x - menu_text.get_width()//2, center_y + 60))
    
    def draw_game_complete(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        font_size = int(36 * self.scaling_system.scale_x)
        font = pygame.font.SysFont(None, font_size)
        
        complete_text = font.render("Игра пройдена! Поздравляем!", True, WHITE)
        restart_text = font.render("Нажмите R для перезапуска", True, WHITE)
        menu_text = font.render("Нажмите M для выхода в меню", True, WHITE)
        
        center_x = WIDTH // 2
        center_y = HEIGHT // 2
        
        screen.blit(complete_text, (center_x - complete_text.get_width()//2, center_y - 50))
        screen.blit(restart_text, (center_x - restart_text.get_width()//2, center_y + 20))
        screen.blit(menu_text, (center_x - menu_text.get_width()//2, center_y + 60))
    
    def handle_input(self):
        """Обработка непрерывного ввода"""
        keys = pygame.key.get_pressed()
        
        if self.game_state == PLAYING:
            if keys[pygame.K_a]:
                self.fire.move(-self.fire.speed, 0)
            if keys[pygame.K_d]:
                self.fire.move(self.fire.speed, 0)
            if keys[pygame.K_LEFT]:
                self.water.move(-self.water.speed, 0)
            if keys[pygame.K_RIGHT]:
                self.water.move(self.water.speed, 0)

# Создание игры
game = Game()
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Обработка событий меню
        if game.game_state in [MENU, SETTINGS]:
            result = game.menu.handle_event(event, game)
            if result == "quit":
                running = False
        
        # Обработка игровых событий
        else:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w and game.game_state == PLAYING:
                    game.fire.jump()
                if event.key == pygame.K_UP and game.game_state == PLAYING:
                    game.water.jump()
                if event.key == pygame.K_F1:
                    game.debug_mode = not game.debug_mode
                if event.key == pygame.K_SPACE and game.game_state == LEVEL_COMPLETE:
                    game.next_level()
                if event.key == pygame.K_r and (game.game_state == GAME_COMPLETE or game.game_state == DEAD):
                    game.load_level(game.current_level)
                if event.key == pygame.K_m and game.game_state in [LEVEL_COMPLETE, DEAD, GAME_COMPLETE, PLAYING]:
                    # Возврат в меню с любой игровой ситуации
                    game.game_state = MENU
                    game.menu.create_main_menu()
    
    # Обработка непрерывного ввода
    game.handle_input()
    
    # Обновление игры
    game.update()
    
    # Отрисовка
    screen.fill(BLACK)
    game.draw()
    
    pygame.display.flip()
    clock.tick(60)

    
pygame.quit()
sys.exit()
