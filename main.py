import pygame
from pygame.locals import *
import os
import random

CELL_SIZE = 32
GRID_WIDTH = 30
GRID_HEIGHT = 30
SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE

RESOURCE_DIR = "resources"


def resource_path(filename):
    return os.path.join(RESOURCE_DIR, filename)


class Food:
    def __init__(self, parent_screen, images):
        self.parent_screen = parent_screen
        self.images = images
        self.image = random.choice(self.images)
        self.x = 0
        self.y = 0

    def draw(self):
        self.parent_screen.blit(self.image, (self.x, self.y))


class Snake:
    def __init__(self, parent_screen):
        self.parent_screen = parent_screen

        self.image_head = pygame.image.load(
            "resources/snake_head.png").convert_alpha()
        self.image_head = pygame.transform.scale(
            self.image_head, (CELL_SIZE, CELL_SIZE))

        self.image_body_stright = pygame.image.load(
            "resources/snake_body_stright.png").convert_alpha()
        self.image_body_stright = pygame.transform.scale(
            self.image_body_stright, (CELL_SIZE, CELL_SIZE))

        self.image_body_curve = pygame.image.load(
            "resources/snake_body_curve.png").convert_alpha()
        self.image_body_curve = pygame.transform.scale(
            self.image_body_curve, (CELL_SIZE, CELL_SIZE))

        self.image_tail = pygame.image.load(
            "resources/snake_tail.png").convert_alpha()
        self.image_tail = pygame.transform.scale(
            self.image_tail, (CELL_SIZE, CELL_SIZE))

        self.direction = 'down'

        self.length = 3
        self.x = [32, 32, 32]
        self.y = [96, 64, 32]

    def move_left(self):
        if self.direction != 'right':
            self.direction = 'left'

    def move_right(self):
        if self.direction != 'left':
            self.direction = 'right'

    def move_up(self):
        if self.direction != 'down':
            self.direction = 'up'

    def move_down(self):
        if self.direction != 'up':
            self.direction = 'down'

    def walk(self):
        # update body
        for i in range(self.length-1, 0, -1):
            self.x[i] = self.x[i-1]
            self.y[i] = self.y[i-1]

        # update head
        if self.direction == 'left':
            self.x[0] -= CELL_SIZE
        if self.direction == 'right':
            self.x[0] += CELL_SIZE
        if self.direction == 'up':
            self.y[0] -= CELL_SIZE
        if self.direction == 'down':
            self.y[0] += CELL_SIZE
        self.draw()

    def draw(self):

        # Draw head rotated
        rotated_head = self.get_rotated_head_image()
        self.parent_screen.blit(rotated_head, (self.x[0], self.y[0]))

        # Draw body stright fragments
        for i in range(1, self.length - 1):
            prev_x, prev_y = self.x[i - 1], self.y[i - 1]
            curr_x, curr_y = self.x[i], self.y[i]
            next_x, next_y = self.x[i + 1], self.y[i + 1]

            if (prev_x == curr_x == next_x) or (prev_y == curr_y == next_y):
                # Stright
                if prev_x == curr_x:
                    img = pygame.transform.rotate(self.image_body_stright, 0)
                else:
                    img = pygame.transform.rotate(self.image_body_stright, 90)
            else:
                # Curve
                if (prev_x < curr_x and next_y < curr_y) or (next_x < curr_x and prev_y < curr_y):
                    angle = 0
                elif (prev_x < curr_x and next_y > curr_y) or (next_x < curr_x and prev_y > curr_y):
                    angle = 90
                elif (prev_x > curr_x and next_y > curr_y) or (next_x > curr_x and prev_y > curr_y):
                    angle = 180
                else:
                    angle = 270
                img = pygame.transform.rotate(self.image_body_curve, angle)

            self.parent_screen.blit(img, (curr_x, curr_y))

        tail_i = self.length - 1
        tail_x, tail_y = self.x[tail_i], self.y[tail_i]
        before_x, before_y = self.x[tail_i - 1], self.y[tail_i - 1]

        if tail_x == before_x:
            tail_rot = 0 if tail_y > before_y else 180
        else:
            tail_rot = 90 if tail_x > before_x else 270

        tail_img = pygame.transform.rotate(self.image_tail, tail_rot)
        self.parent_screen.blit(tail_img, (tail_x, tail_y))

    def get_rotated_head_image(self):
        if self.direction == 'up':
            return pygame.transform.rotate(self.image_head, 0)
        elif self.direction == 'right':
            return pygame.transform.rotate(self.image_head, -90)
        elif self.direction == 'down':
            return pygame.transform.rotate(self.image_head, 180)
        elif self.direction == 'left':
            return pygame.transform.rotate(self.image_head, 90)

    def increase_length(self):
        self.length += 1
        self.x.append(self.x[-1])
        self.y.append(self.y[-1])

    def occupied_cells(self):
        return set(
            (x // CELL_SIZE, y // CELL_SIZE)
            for x, y in zip(self.x, self.y)
        )


class Game:
    def __init__(self):
        pygame.init()

        self.game_state = "RUNNING"

        pygame.display.set_caption("Codebasics Snake And Apple Game")
        self.surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        pygame.mixer.init()
        self.play_background_music()

        self.food_images = (
            [pygame.transform.scale(
                pygame.image.load("resources/Rat_white.png").convert_alpha(), (CELL_SIZE, CELL_SIZE))] * 2 +
            [pygame.transform.scale(
                pygame.image.load("resources/Rat_gray.png").convert_alpha(), (CELL_SIZE, CELL_SIZE))] * 5 +
            [pygame.transform.scale(
                pygame.image.load("resources/Rat_brown.png").convert_alpha(), (CELL_SIZE, CELL_SIZE))] * 8
        )

        self.snake = Snake(self.surface)
        self.snake.draw()
        self.foods = []
        self.spawn_food()
        self.score = 0

        self.clock = pygame.time.Clock()
        self.speed = 5

    def spawn_food(self):
        occupied = self.snake.occupied_cells()
        all_cells = {(x, y) for x in range(GRID_WIDTH)
                     for y in range(GRID_HEIGHT)}
        free_cells = list(all_cells - occupied)

        if not free_cells:
            print("No free cells left. You Won!")
            self.game_state = "GAME_OVER"
            return None

        cell = random.choice(free_cells)
        food = Food(self.surface, self.food_images)
        food.image = random.choice(self.food_images)
        food.x = cell[0] * CELL_SIZE
        food.y = cell[1] * CELL_SIZE
        self.foods.append(food)

    def play_background_music(self):
        pygame.mixer.music.load("resources/background_music.mp3")
        pygame.mixer.music.play(-1)

    def play_sound(self, sound_name):
        if sound_name == "crash":
            sound = pygame.mixer.Sound("resources/crash.mp3")
        elif sound_name == 'ding':
            sound = pygame.mixer.Sound("resources/ding.mp3")

        pygame.mixer.Sound.play(sound)

    def reset(self):
        self.snake = Snake(self.surface)
        self.foods = []
        self.score = 0
        self.speed = 5

    def is_collision(self, x1, y1, x2, y2):
        return x1 == x2 and y1 == y2

    def render_background(self):
        bg = pygame.image.load("resources/background_image.png")
        self.surface.blit(bg, (0, 0))

    def play(self):
        self.render_background()
        self.snake.walk()
        self.position_set = set(zip(self.snake.x, self.snake.y))
        self.display_score()
        head = (self.snake.x[0], self.snake.y[0])

        # Self collision
        if head in self.position_set - {head}:
            self.play_sound("crash")
            self.game_state = "GAME_OVER"
            return

        # Calculate how many rats should be present based on score
        desired_food_count = (self.snake.length - 1) // 10 + 1

        while len(self.foods) < desired_food_count:
            self.spawn_food()
            if self.game_state == "GAME_OVER":
                return

        # Draw all rats and check if snake ate one
        for food in self.foods[:]:
            if self.is_collision(self.snake.x[0], self.snake.y[0], food.x, food.y):
                self.play_sound("ding")
                self.snake.increase_length()
                self.score += 1
                self.foods.remove(food)
                self.speed += 0.4
                self.speed = min(self.speed, 10)
                break
            food.draw()

        # Wall collision
        if (self.snake.x[0] < 0 or self.snake.x[0] >= SCREEN_WIDTH or
                self.snake.y[0] < 0 or self.snake.y[0] >= SCREEN_HEIGHT):
            self.play_sound("crash")
            self.game_state = "GAME_OVER"
            return

        pygame.display.flip()

    def display_score(self):
        font = pygame.font.SysFont('arial', 30)
        score_text = font.render(
            f"Score: {self.score}", True, (200, 200, 200))

        # Rectangle behind the text
        box_x, box_y = SCREEN_WIDTH - 160, 5
        box_w, box_h = 150, 40
        pygame.draw.rect(self.surface, (0, 0, 0), (box_x, box_y, box_w, box_h))
        pygame.draw.rect(self.surface, (255, 255, 255),
                         (box_x, box_y, box_w, box_h), 2)  # border

        # Draw text
        self.surface.blit(score_text, (box_x + 10, box_y + 5))

    def show_game_over(self):
        self.render_background()

        # Draw a box
        box_x, box_y = 150, 250
        box_w, box_h = 700, 200
        pygame.draw.rect(self.surface, (0, 0, 0), (box_x, box_y, box_w, box_h))
        pygame.draw.rect(self.surface, (255, 255, 255),
                         (box_x, box_y, box_w, box_h), 4)  # thicker border

        font = pygame.font.SysFont('arial', 30)
        line1 = font.render(
            f"Game over! Your score is {self.score}", True, (255, 255, 255))
        line2 = font.render(
            "To play again press Enter. To exist press Escape!", True, (255, 255, 255))

        # Centre the text inside the box
        self.surface.blit(line1, (box_x + 20, box_y + 50))
        self.surface.blit(line2, (box_x + 20, box_y + 100))

        pygame.mixer.music.pause()
        self.play_sound("crash")
        pygame.display.flip()

    def run(self):
        self.game_state = "RUNNING"
        running = True
        pause = False

        while running:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False

                    if event.key == K_RETURN:
                        self.reset()
                        pygame.mixer.music.unpause()
                        self.play_background_music()
                        pause = False
                        self.game_state = "RUNNING"

                    if not pause:
                        if event.key == K_LEFT:
                            self.snake.move_left()

                        if event.key == K_RIGHT:
                            self.snake.move_right()

                        if event.key == K_UP:
                            self.snake.move_up()

                        if event.key == K_DOWN:
                            self.snake.move_down()

                elif event.type == QUIT:
                    running = False
            if not pause:
                if self.game_state == "RUNNING":
                    self.play()
                elif self.game_state == "GAME_OVER":
                    self.show_game_over()

            self.clock.tick(int(self.speed))


if __name__ == '__main__':
    game = Game()
    game.run()
