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


class Agent:
    def __init__(self, to_me_queue, from_me_queue, initial_location, initial_visible_map):
        self.to_me_queue = to_me_queue
        self.from_me_queue = from_me_queue
        self.location = initial_location
        self.visible_map = initial_visible_map

    def get_message(self):
        self.to_me_queue.get()

    def put_message(self, message):
        self.from_me_queue.put(message)