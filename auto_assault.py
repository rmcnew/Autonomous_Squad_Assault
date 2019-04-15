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
import logging
import sys
from datetime import datetime
from multiprocessing import Process, Queue

import pygame
from pygame.locals import *

from agent.agent_messages import *
from simulation.drawable import Drawable
from simulation.missionmap import MissionMap
from opfor.opfor import Opfor
from graphics.pygame_constants import *
from warbot.warbot import Warbot
from warbot.warbot_radio_broker import WarbotRadioBroker


class AutoAssault:
    """Autonomous Assault Simulation"""
    def __init__(self, args):
        self.start_time = None
        # generate map
        self.mission_map = MissionMap()
        self.mission_map.populate_map(args)
        # create IPC queues and warbot radio message broker
        self.to_agent_queues = []
        self.to_all_warbots_queue = Queue()
        self.warbot_radio_broker = WarbotRadioBroker(self.to_all_warbots_queue)
        self.warbot_radio_broker_process = Process(target=self.warbot_radio_broker.run)
        # create containers for child processes and objects
        self.processes = []
        self.warbots = []
        self.opfors = []
        self.agents = []  # includes all live warbots and opfors
        self.civilians = []  # civilians are not agents (no child processes)

# simulation setup methods
    def create_warbots(self, to_sim_queue):
        """Create warbot objects and associated child processes"""
        logging.debug("Creating {} warbots".format(len(self.mission_map.warbot_locations)))
        for location in self.mission_map.warbot_locations:
            to_queue = Queue()
            self.to_agent_queues.append(to_queue)
            visible_map = self.mission_map.get_visible_map_around_point(location, WARBOT_VISION_DISTANCE)
            name = self.mission_map.get_named_drawable_at_location(location, WARBOT_PREFIX)
            logging.info("Creating warbot {} at location {}".format(name, location))
            to_this_warbot_queue = Queue()
            warbot = Warbot(to_queue, to_sim_queue, location, visible_map, name, to_this_warbot_queue, self.warbot_radio_broker)
            self.warbots.append(warbot)
            process = Process(target=warbot.run)
            self.processes.append(process)

    def create_opfor(self, to_sim_queue):
        """Create OPFOR objects and associated child processes"""
        logging.debug("Creating {} OPFOR".format(len(self.mission_map.opfor_locations)))
        for location in self.mission_map.opfor_locations:
            to_queue = Queue()
            self.to_agent_queues.append(to_queue)
            visible_map = self.mission_map.get_visible_map_around_point(location, OPFOR_VISION_DISTANCE)
            name = self.mission_map.get_named_drawable_at_location(location, OPFOR_PREFIX)
            logging.info("Creating OPFOR {} at location {}".format(name, location))
            opfor = Opfor(to_queue, to_sim_queue, location, visible_map, name)
            self.opfors.append(opfor)
            process = Process(target=opfor.run)
            self.processes.append(process)

    def create_civilians(self):
        """Create civilian objects"""
        None  # stubbed out for now

# pygame drawing and event handling
    def check_for_quit(self):
        """See if the user indicated quit ('q' key, ESC key, or clicked window close button"""
        for event in pygame.event.get():  # event handling loop
            if event.type == QUIT:
                self.terminate()
            elif event.type == KEYDOWN and (event.key == K_q or event.key == K_ESCAPE):
                self.terminate()

    def draw_grid(self, mission_map):
        """Draw the map grid via pygame"""
        # draw gridlines
        for x in range(0, WINDOW_WIDTH, CELL_SIZE):  # draw vertical lines
            pygame.draw.line(DISPLAY_SURF, Colors.DARK_GRAY.value, (x, TOP_BUFFER), (x, WINDOW_HEIGHT + TOP_BUFFER))
        for y in range(TOP_BUFFER, WINDOW_HEIGHT, CELL_SIZE):  # draw horizontal lines
            pygame.draw.line(DISPLAY_SURF, Colors.DARK_GRAY.value, (0, y), (WINDOW_WIDTH, y))
        # draw grid objects
        for x in range(0, mission_map.grid.width):
            for y in range(0, mission_map.grid.height):
                if mission_map.grid.array[x][y] != 0:  # use the internal array directly for speed
                    (lineColor, fillColor) = Drawable(mission_map.grid.array[x][y]).color
                    cell_x = x * CELL_SIZE
                    cell_y = y * CELL_SIZE + TOP_BUFFER
                    rect = pygame.Rect(cell_x, cell_y, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(DISPLAY_SURF, lineColor.value, rect)
                    inner_rect = pygame.Rect(cell_x + 4, cell_y + 4, CELL_SIZE - 8, CELL_SIZE - 8)
                    pygame.draw.rect(DISPLAY_SURF, fillColor.value, inner_rect)

    def check_for_key_press(self):
        """See if the user pressed any key to quit at simulation over"""
        if len(pygame.event.get(QUIT)) > 0:
            self.terminate()
        key_up_events = pygame.event.get(KEYUP)
        if len(key_up_events) == 0:
            return None
        if key_up_events[0].key == K_ESCAPE:
            self.terminate()
        return key_up_events[0].key

    def draw_press_key_message(self):
        """Draw a message indicating how to end the simulation"""
        press_key_surf = BASIC_FONT.render('Press a key to quit', True, Colors.DARK_GRAY.value)
        press_key_rect = press_key_surf.get_rect()
        press_key_rect.topleft = (WINDOW_WIDTH - 200, WINDOW_HEIGHT - 30)
        DISPLAY_SURF.blit(press_key_surf, press_key_rect)

    def draw_legend(self):
        """Draw a legend that shows what map colors represent"""
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

    def show_game_over_screen(self, winner):
        """Draw simulation ended message"""
        game_over_font = pygame.font.Font(SANS_FONT, 150)
        game_surf = game_over_font.render(winner, True, Colors.WHITE.value)
        over_surf = game_over_font.render('Wins!', True, Colors.WHITE.value)
        game_rect = game_surf.get_rect()
        over_rect = over_surf.get_rect()
        game_rect.midtop = (WINDOW_WIDTH / 2, 10)
        over_rect.midtop = (WINDOW_WIDTH / 2, game_rect.height + 10 + 25)

        DISPLAY_SURF.blit(game_surf, game_rect)
        DISPLAY_SURF.blit(over_surf, over_rect)
        self.draw_press_key_message()
        pygame.display.update()
        pygame.time.wait(500)
        self.check_for_key_press()  # clear out any key presses in the event queue
        while True:
            if self.check_for_key_press():
                pygame.event.get()  # clear event queue
                return

    def update_display(self):
        """Draw the updated game state (mission_map) to the screen"""
        DISPLAY_SURF.fill(BG_COLOR.value)
        self.draw_grid(self.mission_map)
        elapsed_minutes = int((datetime.now() - self.start_time).seconds / SECONDS_PER_MINUTE)
        # draw_legend()
        pygame.display.update()
        FPS_CLOCK.tick(FPS)

# simulation main loop and helpers
    def terminate(self):
        """Simulation shutdown and clean-up"""
        logging.debug("Sending shutdown message to child processes . . .")
        for to_agent_queue in self.to_agent_queues:
            to_agent_queue.put(shutdown_message())
        self.to_all_warbots_queue.put(shutdown_message())
        logging.debug("Waiting for child processes to shutdown . . .")
        for process in self.processes:
            process.join()
        self.warbot_radio_broker_process.join()
        logging.debug("Quitting . . .")
        logging.shutdown()
        pygame.quit()
        sys.exit()

    def update_mission_map(self, messages_received):
        """Update game state (mission_map) from agent subprocess messages"""
        for message in messages_received:
            logging.debug("Received message: {}".format(message))

    def start_child_processes(self):
        """Start child processes running for agents and warbot radio broker process"""
        self.warbot_radio_broker_process.start()
        # start warbot and opfor processes running
        for process in self.processes:
            process.start()
        self.start_time = datetime.now()

    def run_simulation(self, to_sim_queue):
        """Main simulation loop"""
        self.start_child_processes()
        mission_complete = False
        quit_wanted = False
        live_process_count = len(self.processes)
        while not mission_complete and not quit_wanted:  # main game loop
            # check for q or Esc keypress or window close events to quit
            self.check_for_quit()
            messages_received = []
            # send out "your_turn" messages to agents

            for to_agent_queue in self.to_agent_queues:
                to_agent_queue.put(your_turn_message())
            # await "take_turn" response messages
            logging.debug("Waiting on responses . . .")
            while len(messages_received) < live_process_count:
                message = to_sim_queue.get()
                messages_received.append(message)
            logging.debug("Done waiting on responses.  Updating mission_map")
            # update mission_map
            self.update_mission_map(messages_received)
            # update display
            self.update_display()
        # after the mission is complete or quit is indicated, clean-up and shutdown
        self.terminate()


def parse_arguments():
    """Parse the command line arguments"""
    # setup command line argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', default=5, type=int, choices=range(1, 12),
                        help='number of rifle warbots (1 to 11)')
    parser.add_argument('-e', default=5, type=int, choices=range(1, 12),
                        help='number of enemies (1 to 11)')
    parser.add_argument('-c', default=5, type=int, choices=range(0, 21),
                        help='number of civilians (0 to 20)')
    return parser.parse_args()


def setup_pygame():
    """Setup global PyGame state"""
    global FPS_CLOCK, DISPLAY_SURF, BASIC_FONT, SCORE_FONT
    pygame.init()
    FPS_CLOCK = pygame.time.Clock()
    DISPLAY_SURF = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT + TOP_BUFFER + BOTTOM_BUFFER))
    BASIC_FONT = pygame.font.Font(SANS_FONT, 24)
    SCORE_FONT = pygame.font.Font(SANS_FONT, 36)
    pygame.display.set_caption(AUTO_ASSAULT)


def main():
    """Main entry point"""
    # start logging
    log_file = "Auto_Assault.log"
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d : %(message)s',
                        filename=log_file,
                        level=logging.DEBUG)
    # parse command line args
    args = parse_arguments()

    # setup simulation
    auto_assault = AutoAssault(args)
    to_sim_queue = Queue()

    # create warbots
    auto_assault.create_warbots(to_sim_queue)
    # create opfor
    auto_assault.create_opfor(to_sim_queue)
    # create civilians
    auto_assault.create_civilians()

    # pygame setup
    setup_pygame()

    # run the simulation
    auto_assault.run_simulation(to_sim_queue)




if __name__ == '__main__':
    main()
