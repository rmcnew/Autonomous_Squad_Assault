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
import json
import logging
from warbot.warbot_radio_broker import WarbotRadioBroker
from shared.constants import *


class WarbotRadio:
    """Simulates tactical radio used by warbots for communication"""

    def __init__(self, name, to_this_warbot_queue, warbot_radio_broker):
        self.name = name
        self.to_this_warbot_queue = to_this_warbot_queue
        self.warbot_radio_broker= warbot_radio_broker
        warbot_radio_broker.subscribe(name, self.to_this_warbot_queue)

    def send(self, message):
        # logging.debug("Sending message: {}".format(message))
        self.warbot_radio_broker.to_all_warbots_queue.put_nowait(message)

    def receive(self):
        message = json.loads(self.to_this_warbot_queue.get())
        if FROM in message and message[FROM] == self.name:
            return None
        # logging.debug("Received message: {}".format(message))
        return message

    def messages_ready(self):
        return not self.to_this_warbot_queue.empty()

    def receive_messages(self):
        messages = []
        while self.messages_ready():
            message = self.receive()
            if message is not None:
                messages.append(message)
        return messages

    def shutdown(self):
        self.warbot_radio_broker.unsubscribe(self.name)



