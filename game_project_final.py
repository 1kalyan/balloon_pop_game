import pygame
import random

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
SKY_BLUE = (135, 206, 235)
BOMB_COLOR = (169, 169, 169)  # Dark grey for bombs

# Font
font = pygame.font.SysFont(None, 55)

# Balloon settings
balloon_width = 50
balloon_height = 70
balloon_colors = [RED, GREEN, BLUE]

# Clock
clock = pygame.time.Clock()


class GameObject:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.image = None
        self.rect = None

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, self.rect)


class Balloon(GameObject):
    def __init__(self, x, y, speed, color):
        super().__init__(x, y)
        self.color = color
        self.speed = speed
        self.image = pygame.Surface((balloon_width, balloon_height), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, self.color, [0, 0, balloon_width, balloon_height])
        self.rect = self.image.get_rect(topleft=(x, y))

    def move(self):
        self.y -= self.speed
        self.rect.y = self.y

    def is_popped(self, pos):
        return self.rect.collidepoint(pos)


class BombBalloon(Balloon):
    def __init__(self, x, y, speed):
        super().__init__(x, y, speed + 1, BOMB_COLOR)


class Background(GameObject):
    def __init__(self):
        super().__init__(0, 0)
        self.image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.image.fill(SKY_BLUE)
        self.rect = self.image.get_rect()

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class TextObject(GameObject):
    def __init__(self, x, y, text, font, color):
        super().__init__(x, y)
        self.text = text
        self.font = font
        self.color = color
        self.image = self.font.render(self.text, True, self.color)
        self.rect = self.image.get_rect(center=(x, y))

    def update_text(self, text):
        self.text = text
        self.image = self.font.render(self.text, True, self.color)
        self.rect = self.image.get_rect(center=self.rect.center)


class Level:
    def __init__(self, name, balloon_speed):
        self.name = name
        self.balloon_speed = balloon_speed


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.background = Background()
        self.levels = {
            'easy': Level('Easy', 2),
            'medium': Level('Medium', 4),
            'hard': Level('Hard', 6)
        }
        self.balloons = []
        self.score = 0
        self.game_active = False

    def create_balloon(self, speed):
        x = random.randint(0, SCREEN_WIDTH - balloon_width)
        y = SCREEN_HEIGHT
        color = random.choice(balloon_colors)
        if random.random() < 0.1:  # 10% chance to create a bomb balloon
            return BombBalloon(x, y, speed)
        else:
            return Balloon(x, y, speed, color)

    def start_game(self, level):
        self.balloons = [self.create_balloon(level.balloon_speed) for _ in range(5)]
        self.score = 0
        self.game_active = True

    def update(self):
        if self.game_active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    for balloon in self.balloons[:]:
                        if balloon.is_popped(pos):
                            if isinstance(balloon, BombBalloon):
                                self.game_active = False
                            else:
                                self.balloons.remove(balloon)
                                self.balloons.append(self.create_balloon(self.levels['easy'].balloon_speed))
                                self.score += 1

            for balloon in self.balloons[:]:
                balloon.move()
                if balloon.y < -balloon_height:
                    if not isinstance(balloon, BombBalloon):
                        self.game_active = False
                    else:
                        self.balloons.remove(balloon)
                        self.balloons.append(self.create_balloon(self.levels['easy'].balloon_speed))

        return True

    def draw(self):
        self.background.draw(self.screen)

        for balloon in self.balloons:
            balloon.draw(self.screen)

        score_text = TextObject(70, 20, f"Score: {self.score}", font, WHITE)
        score_text.draw(self.screen)

        pygame.display.flip()
        clock.tick(30)


class Menu:
    def __init__(self, screen, levels):
        self.screen = screen
        self.levels = levels
        self.menu_font = pygame.font.SysFont(None, 75)
        self.menu_objects = [
            TextObject(SCREEN_WIDTH // 2, 50, "Choose Difficulty", self.menu_font, WHITE),
            TextObject(SCREEN_WIDTH // 2, 200, "Easy - Level 1", self.menu_font, WHITE),
            TextObject(SCREEN_WIDTH // 2, 300, "Medium - Level 2", self.menu_font, WHITE),
            TextObject(SCREEN_WIDTH // 2, 400, "Hard - Level 3", self.menu_font, WHITE),
            TextObject(SCREEN_WIDTH // 2, 500, "Exit", self.menu_font, WHITE)
        ]

    def draw(self):
        for obj in self.menu_objects:
            obj.rect.centerx = SCREEN_WIDTH // 2
            obj.draw(self.screen)
        pygame.display.flip()

    def show(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return None
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if 150 <= pos[1] <= 250:
                        return self.levels['easy']
                    elif 250 <= pos[1] <= 350:
                        return self.levels['medium']
                    elif 350 <= pos[1] <= 450:
                        return self.levels['hard']
                    elif 450 <= pos[1] <= 550:
                        pygame.quit()
                        return None
            self.draw()


def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Balloon Pop Game")

    game = Game(screen)
    menu = Menu(screen, game.levels)

    while True:
        selected_level = menu.show()
        if selected_level is None:
            break  # Exit the game
        game.start_game(selected_level)
        while game.update():
            game.draw()
            if not game.game_active:
                break

    pygame.quit()


if __name__ == "__main__":
    main()
