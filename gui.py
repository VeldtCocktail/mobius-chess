import sys
import math
import pygame
from main import Game, Board, Piece

class GUI():
    SCREEN_SIZE = (1280, 680)
    CENTER = (SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2)
    CIRCLE_RADIUS_UNIT = min(SCREEN_SIZE[0], SCREEN_SIZE[1]) // (2.2 * 5)

    def __init__(self, game:Game):
        pygame.init()

        self.game = game
        self.screen = pygame.display.set_mode(self.SCREEN_SIZE)
        self.clock = pygame.time.Clock()
        self.running = True

    def render_circular_board(self):
        def ct_circle(radius_units):
            pygame.draw.circle(
                self.screen, "black", self.CENTER,
                self.CIRCLE_RADIUS_UNIT * radius_units, 2
            )

        def ct_line(angle):
            x_a = self.CIRCLE_RADIUS_UNIT * math.cos(math.radians(angle))
            y_a = self.CIRCLE_RADIUS_UNIT * math.sin(math.radians(angle))

            x_b = (5 * self.CIRCLE_RADIUS_UNIT) * math.cos(math.radians(angle))
            y_b = (5 * self.CIRCLE_RADIUS_UNIT) * math.sin(math.radians(angle))

            pygame.draw.line(
                self.screen, "black",
                (
                    self.CENTER[0] + x_a,
                    self.CENTER[1] - y_a
                ),
                (
                    self.CENTER[0] + x_b,
                    self.CENTER[1] - y_b
                ),
                2
            )

        for r in range(1, 6):
            ct_circle(r)

        for da in range(0, 3600, 225):
            ct_line(da / 10)

    def render_colored_circular_board(self):
        def ct_ring_sector(r_units, start_angle, color):
            outer_r = r_units * self.CIRCLE_RADIUS_UNIT
            inner_r = outer_r - self.CIRCLE_RADIUS_UNIT

            ds_angle = int(10 * start_angle)
            de_angle = int(10 * (start_angle + 22.5))

            points = []

            step = 1 # degrees

            for angle in range(ds_angle, de_angle + step, step * 5):
                x = self.CENTER[0] + outer_r * math.cos(math.radians(angle / 10))
                y = self.CENTER[1] - outer_r * math.sin(math.radians(angle / 10))
                points.append((x, y))

            for angle in range(de_angle, ds_angle - step, -5 * step):
                x = self.CENTER[0] + inner_r * math.cos(math.radians(angle / 10))
                y = self.CENTER[1] - inner_r * math.sin(math.radians(angle / 10))
                points.append((x, y))

            pygame.draw.polygon(self.screen, color, points)

        for u in range(2, 6):
            offset = 0 if u % 2 else 225

            for da in range(offset, 3600, 450):
                ct_ring_sector(u, da / 10, "grey")

    def main_loop(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.screen.fill("white")

            self.render_colored_circular_board()
            self.render_circular_board()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    gui = GUI(game)
    gui.main_loop()