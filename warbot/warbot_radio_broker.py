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

# agent is an autonomous actor in the simulation
# it is implemented as a subprocess of the main simulation
# process so that it can run independently
# it communicates with the main simulation process via two
# python multiprocessing queues

# agents communicate with the main simulation process to
# take their turn in the simulation:  they receive a
# structured message with their current location and
# visible map around them.  The respond with the action
# they decide to take during that turn
import json
import logging
from shared.constants import *


class WarbotRadioBroker:
    """Process that simulates radio broadcasts by relaying messages from a centralized radio Queue to other Queues"""
    def __init__(self, to_all_warbots_queue):
        self.to_all_warbots_queue = to_all_warbots_queue
        self.individual_warbot_queues = {}

    def subscribe(self, name, individual_warbot_queue):
        logging.debug("Subscribing {} to warbot radio".format(name))
        self.individual_warbot_queues[name] = individual_warbot_queue

    def unsubscribe(self, name):
        if name in self.individual_warbot_queues:
            logging.debug("Unsubscribing {} from warbot radio".format(name))
            del self.individual_warbot_queues[name]
        else:
            logging.warn("{} was not subscribed to warbot radio".format(name))

    def run(self):
        while True:
            raw_message = self.to_all_warbots_queue.get()
            message = json.loads(raw_message)
            if message[MESSAGE_TYPE] == SHUTDOWN:
                logging.debug("WarbotRadioBroker received shutdown message.  Shutting down . . .")
                break
            for warbot_queue in self.individual_warbot_queues.values():
                warbot_queue.put_nowait(raw_message)

