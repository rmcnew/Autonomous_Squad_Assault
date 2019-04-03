# Autonomous Squad Assault
# Copyright (C) 2019  Richard Scott McNew.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import argparse
import sys
from datetime import datetime

import pygame
from pygame.locals import *

from missionmap import MissionMap
from grid import Grid
from a_star import *

# setup command line argument parsing
parser = argparse.ArgumentParser()
parser.add_argument('-r', default=5, type=int, choices=range(1, 7),
                    help='number of rifle warbots (1 to 6)')
parser.add_argument('-s', default=2, type=int, choices=range(1, 5),
                    help='number of SAW (light machine gun) warbots (1 to 4)')
parser.add_argument('-g', default=2, type=int, choices=range(1, 5),
                    help='number of grenadier warbots (1 to 4)')
parser.add_argument('-u', default=2, type=int, choices=range(1, 5),
                    help='number of UAV scouts (1 to 4)')
parser.add_argument('-e', default=5, type=int, choices=range(1, 10),
                    help='number of enemies (1 to 9)')
parser.add_argument('-c', default=5, type=int, choices=range(0, 21),
                    help='number of civilians (0 to 20)')
args = parser.parse_args()

# create grid
grid = Grid()

# generate map:
mission_map = MissionMap(grid, args)


def main():
    global FPS_CLOCK, DISPLAY_SURF, BASIC_FONT, SCORE_FONT
    pygame.init()
    FPS_CLOCK = pygame.time.Clock()
    DISPLAY_SURF = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT + TOP_BUFFER + BOTTOM_BUFFER))
    BASIC_FONT = pygame.font.Font(SANS_FONT, 24)
    SCORE_FONT = pygame.font.Font(SANS_FONT, 36)
    pygame.display.set_caption(AUTO_ASSAULT)
    run_game()


def check_for_quit():
    for event in pygame.event.get():  # event handling loop
        if event.type == QUIT:
            terminate()
        elif event.type == KEYDOWN and (event.key == K_q or event.key == K_ESCAPE):
            terminate()


def get_winner(scores):
    winner_index = 0
    winner_score = 0
    for index, score in enumerate(scores):
        if score > winner_score:
            winner_index = index
            winner_score = score
    return winner_index


def run_game():
    start_time = datetime.now()
    mission_complete = False
    while not mission_complete:  # main game loop
        # check for q or Esc keypress or window close events to quit
        check_for_quit()
        # warbots decide and move
        # for warbot in warbots:
        #    warbot.run(grid)
        # move dogs
        # for op in opfor:
        #    op.run(grid)

        # update display
        DISPLAY_SURF.fill(BG_COLOR.value)
        draw_grid()
        # quit if the room is clean
        elapsed_minutes = int((datetime.now() - start_time).seconds / SECONDS_PER_MINUTE)

        #draw_legend()
        pygame.display.update()
        FPS_CLOCK.tick(FPS)
    #winner_index = get_winner(scores)
    #show_game_over_screen(Drawable(winner_index + 12).name)


def terminate():
    pygame.quit()
    sys.exit()


def draw_grid():
    # draw gridlines
    for x in range(0, WINDOW_WIDTH, CELL_SIZE):  # draw vertical lines
        pygame.draw.line(DISPLAY_SURF, Colors.DARK_GRAY.value, (x, TOP_BUFFER), (x, WINDOW_HEIGHT + TOP_BUFFER))
    for y in range(TOP_BUFFER, WINDOW_HEIGHT, CELL_SIZE):  # draw horizontal lines
        pygame.draw.line(DISPLAY_SURF, Colors.DARK_GRAY.value, (0, y), (WINDOW_WIDTH, y))
    # draw grid objects
    for x in range(0, grid.width):
        for y in range(0, grid.height):
            if grid.array[x][y] != 0:  # use the internal array directly for speed
                (lineColor, fillColor) = Drawable(grid.array[x][y]).color
                cell_x = x * CELL_SIZE
                cell_y = y * CELL_SIZE + TOP_BUFFER
                rect = pygame.Rect(cell_x, cell_y, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(DISPLAY_SURF, lineColor.value, rect)
                inner_rect = pygame.Rect(cell_x + 4, cell_y + 4, CELL_SIZE - 8, CELL_SIZE - 8)
                pygame.draw.rect(DISPLAY_SURF, fillColor.value, inner_rect)


def draw_score(elapsed_minutes):
    None
    # opfor_left = get_opfor_alive_count()
    # scores = []
    # for robovac in robovacs:
    #     score = int(robovac.score(dirty_left, filthy_left, elapsed_minutes))
    #     scores.append(score)
    #     surf = SCORE_FONT.render('Score: %s' % str(score),
    #                              True,
    #                              robovac.name.color[0].value)
    #     rect = surf.get_rect()
    #     rect.topleft = robovac.score_position
    #     DISPLAY_SURF.blit(surf, rect)
    # return int(dirty_left + filthy_left) > 0, scores


def draw_legend():
    x = 7
    for index in range(1, 10):
        drawable = Drawable(index)
        surf = BASIC_FONT.render(drawable.name, True, drawable.color[0].value)
        rect = surf.get_rect()
        rect.topleft = (x, TOP_BUFFER + WINDOW_HEIGHT + 15)
        DISPLAY_SURF.blit(surf, rect)
        x = x + LEGEND_SCALE * len(drawable.name) + 7
    x = 7
    for index in range(10, 18):
        drawable = Drawable(index)
        surf = BASIC_FONT.render(drawable.name, True, drawable.color[0].value)
        rect = surf.get_rect()
        rect.topleft = (x, TOP_BUFFER + WINDOW_HEIGHT + 60)
        DISPLAY_SURF.blit(surf, rect)
        x = x + LEGEND_SCALE * len(drawable.name) + 7


def check_for_key_press():
    if len(pygame.event.get(QUIT)) > 0:
        terminate()

    key_up_events = pygame.event.get(KEYUP)
    if len(key_up_events) == 0:
        return None
    if key_up_events[0].key == K_ESCAPE:
        terminate()
    return key_up_events[0].key


def draw_press_key_message():
    press_key_surf = BASIC_FONT.render('Press a key to quit', True, Colors.DARK_GRAY.value)
    press_key_rect = press_key_surf.get_rect()
    press_key_rect.topleft = (WINDOW_WIDTH - 200, WINDOW_HEIGHT - 30)
    DISPLAY_SURF.blit(press_key_surf, press_key_rect)


def show_game_over_screen(winner):
    game_over_font = pygame.font.Font(SANS_FONT, 150)
    game_surf = game_over_font.render(winner, True, Colors.WHITE.value)
    over_surf = game_over_font.render('Wins!', True, Colors.WHITE.value)
    game_rect = game_surf.get_rect()
    over_rect = over_surf.get_rect()
    game_rect.midtop = (WINDOW_WIDTH / 2, 10)
    over_rect.midtop = (WINDOW_WIDTH / 2, game_rect.height + 10 + 25)

    DISPLAY_SURF.blit(game_surf, game_rect)
    DISPLAY_SURF.blit(over_surf, over_rect)
    draw_press_key_message()
    pygame.display.update()
    pygame.time.wait(500)
    check_for_key_press()  # clear out any key presses in the event queue

    while True:
        if check_for_key_press():
            pygame.event.get()  # clear event queue
            return


if __name__ == '__main__':
    main()
