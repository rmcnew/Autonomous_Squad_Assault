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
import logging
from agent.agent import Agent
from direction import Direction
from agent.agent_messages import *


class Opfor(Agent):

    def __init__(self, to_me_queue, from_me_queue, initial_location, initial_visible_map, name):
        Agent.__init__(self, to_me_queue, from_me_queue, initial_location, initial_visible_map, name)
        self.direction = Direction.EAST
        self.action_queue = []
        self.path = []

    def run(self):
        log_file = "{}.log".format(self.name)
        logging.basicConfig(format='%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d : %(message)s',
                            filename=log_file,
                            level=logging.DEBUG)
        run_simulation = True
        while run_simulation:
            # get message from to_me_queue
            message = self.get_sim_message()
            if message[MESSAGE_TYPE] == SHUTDOWN:
                run_simulation = False
            logging.debug("Received message: {}".format(message))
            self.put_sim_message(take_turn_message(self.name, "Hello from {}".format(self.name)))