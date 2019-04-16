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
from agent.agent_messages import *
from warbot.warbot_messages import *
from warbot.warbot_radio import WarbotRadio


class Warbot(Agent):
    """Represents an autonomous robotic warrior"""
    def __init__(self, to_me_queue, from_me_queue, initial_location, initial_visible_map, name,
                 to_this_warbot_queue, warbot_radio_broker):
        Agent.__init__(self, to_me_queue, from_me_queue, initial_location,
                       initial_visible_map, WARBOT_VISION_DISTANCE, name)
        self.radio = WarbotRadio(self.name, to_this_warbot_queue, warbot_radio_broker)
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
            elif sim_message[MESSAGE_TYPE] == YOUR_TURN:
                self.update_location_and_visible_map(sim_message[VISIBLE_MAP])
                self.visible_map.scan()
                logging.debug("{}: I see {} warbots nearby".format(self.name, len(self.visible_map.warbot_locations)))
                self.put_sim_message(take_turn_message(self.name, "Hello!"))

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

