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
import random
from math import fabs
import logging
from agent.action import Action
from agent.agent import Agent
from simulation.direction import Direction
from agent.agent_messages import *
from warbot.warbot_radio import WarbotRadio
from warbot.warbot_messages import *


class Warbot(Agent):
    """Represents an autonomous robotic warrior"""
    def __init__(self, to_me_queue, from_me_queue, initial_location, initial_visible_map, name,
                 to_this_warbot_queue, warbot_radio_broker):
        Agent.__init__(self, to_me_queue, from_me_queue, initial_location, initial_visible_map, name)
        self.radio = WarbotRadio(self.name, to_this_warbot_queue, warbot_radio_broker)
        self.direction = Direction.EAST
        self.action_queue = []
        self.path = []
        self.run_simulation = True

    def shutdown(self):
        """Clean up resources and shutdown"""
        logging.debug("{} shutting down".format(self.name))
        self.radio.shutdown()

    def handle_warbot_messages(self, warbot_messages):
        for warbot_message in warbot_messages:
            logging.debug("{}: Received warbot_message: {}".format(self.name, warbot_message))

    def handle_sim_messages(self, sim_messages):
        for sim_message in sim_messages:
            logging.debug("{}: Received sim_message: {}".format(self.name, sim_message))
            if sim_message[MESSAGE_TYPE] == SHUTDOWN:
                logging.debug("{} received shutdown message".format(self.name))
                self.run_simulation = False
            logging.debug("Received sim_message: {}".format(sim_message))
            self.put_sim_message(take_turn_message(self.name, "Hello from {}".format(self.name)))

    def run(self):
        # notify other warbots that this warbot is operational
        self.radio.send(warbot_online_message(self.name))
        while self.run_simulation:
            # get and handle warbot messages
            warbot_messages = self.radio.receive_messages()
            self.handle_warbot_messages(warbot_messages)

            # get and handle simulation messages
            sim_messages = self.receive_sim_messages()
            self.handle_sim_messages(sim_messages)
        self.shutdown()

    def next_action_from_path(self, current_point, next_point):
        delta_x = next_point.x - current_point.x
        if fabs(delta_x) > 1:
            delta_x = int(delta_x / fabs(delta_x))
        delta_y = next_point.y - current_point.y
        if fabs(delta_y) > 1:
            delta_y = int(delta_y / fabs(delta_y))
        next_dir = "turn_{}".format(Direction((delta_x, delta_y)).name).upper()
        self.action_queue.append(Action[next_dir])
        self.action_queue.append(Action["MOVE_FORWARD"])

    def do_action(self, action, grid):
        if action is Action.MOVE_FORWARD or action is Action.MOVE_BACKWARD:
            getattr(self, action.value)(grid)
        else:
            getattr(self, action.value)()

    def turn_north(self):
        self.direction = Direction.NORTH

    def turn_northeast(self):
        self.direction = Direction.NORTHEAST

    def turn_east(self):
        self.direction = Direction.EAST

    def turn_southeast(self):
        self.direction = Direction.SOUTHEAST

    def turn_south(self):
        self.direction = Direction.SOUTH

    def turn_southwest(self):
        self.direction = Direction.SOUTHWEST

    def turn_west(self):
        self.direction = Direction.WEST

    def turn_northwest(self):
        self.direction = Direction.NORTHWEST

    def turn_left(self):
        if self.direction is Direction.NORTH:
            self.direction = Direction.WEST
        elif self.direction is Direction.NORTHEAST:
            self.direction = Direction.NORTHWEST
        elif self.direction is Direction.EAST:
            self.direction = Direction.NORTH
        elif self.direction is Direction.SOUTHEAST:
            self.direction = Direction.NORTHEAST
        elif self.direction is Direction.SOUTH:
            self.direction = Direction.EAST
        elif self.direction is Direction.SOUTHWEST:
            self.direction = Direction.SOUTHEAST
        elif self.direction is Direction.WEST:
            self.direction = Direction.SOUTH
        elif self.direction is Direction.NORTHWEST:
            self.direction = Direction.SOUTHWEST

    def turn_right(self):
        if self.direction is Direction.NORTH:
            self.direction = Direction.EAST
        elif self.direction is Direction.NORTHEAST:
            self.direction = Direction.SOUTHEAST
        elif self.direction is Direction.EAST:
            self.direction = Direction.SOUTH
        elif self.direction is Direction.SOUTHEAST:
            self.direction = Direction.SOUTHWEST
        elif self.direction is Direction.SOUTH:
            self.direction = Direction.WEST
        elif self.direction is Direction.SOUTHWEST:
            self.direction = Direction.NORTHWEST
        elif self.direction is Direction.WEST:
            self.direction = Direction.NORTH
        elif self.direction is Direction.NORTHWEST:
            self.direction = Direction.NORTHEAST

    def turn_random(self):
        index = random.randint(0, 7)
        current_index = 0
        for direction in Direction:
            if current_index == index:
                getattr(self, "turn_{}".format(direction.name.lower()))()
            current_index = current_index + 1

    # def move_forward(self, grid):
    #     next_location = self.location.plus(self.direction)
    #     if can_enter(grid, next_location):
    #         grid.enter(next_location, self.name)
    #         grid.exit(self.location, self.name)
    #         # update internal location
    #         self.location = next_location
    #     else:  # cannot move up, back off and change direction
    #         self.action_queue.insert(0, Action.TURN_LEFT)
    #
    # def move_backward(self, grid):
    #     next_location = self.location.minus(self.direction)
    #     if can_enter(grid, next_location):
    #         grid.enter(next_location, self.name)
    #         grid.exit(self.location, self.name)
    #         self.location = next_location
    #     else:  # cannot move up, back off and change direction
    #         self.action_queue.insert(0, Action.TURN_LEFT)

    def old_run(self, grid):  # take a turn
        # if there are pending actions do them first
        if len(self.action_queue) > 0:
            action = self.action_queue.pop(0)
            self.do_action(action, grid)
        # if following a path, get the next point
        # and queue the next actions to move there
        elif len(self.path) > 0:
            next_point = self.path.pop(0)
            self.next_action_from_path(self.location, next_point)
            action = self.action_queue.pop(0)
            self.do_action(action, grid)
