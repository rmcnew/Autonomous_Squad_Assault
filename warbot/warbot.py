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
from time import sleep

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
        self.warbot_names = []
        self.squad_leader = None
        self.team_a_leader = None
        self.team_a = []
        self.team_b_leader = None
        self.team_b = []

    def i_am_squad_leader(self):
        return self.squad_leader is not None and self.squad_leader == self.name

    def i_am_team_a_leader(self):
        return self.team_a_leader is not None and self.team_a_leader == self.name

    def i_am_team_b_leader(self):
        return self.team_b_leader is not None and self.team_b_leader == self.name

    def i_am_on_team_a(self):
        return self.name in self.team_a

    def i_am_on_team_b(self):
        return self.name in self.team_b

    def get_role_name(self):
        if self.i_am_squad_leader():
            return SQUAD_LEADER
        elif self.i_am_team_a_leader():
            return "{} . My team is: {}".format(TEAM_A_LEADER, self.team_a)
        elif self.i_am_team_b_leader():
            return "{} . My team is: {}".format(TEAM_B_LEADER, self.team_b)
        elif self.i_am_on_team_a():
            return ON_TEAM_A
        elif self.i_am_on_team_b():
            return ON_TEAM_B

    def shutdown(self):
        """Clean up resources and shutdown"""
        logging.debug("{} shutting down".format(self.name))
        self.radio.shutdown()

    def extract_id_from_warbot_name(self, name):
        """Get a warbot ID from the warbot name"""
        return int(name[len(WARBOT_PREFIX):])

    def compare_ids(self, their_id):
        return int(self.extract_id_from_warbot_name(self.name)) < their_id

    def conduct_election(self):
        logging.debug("{}: Conducting leader election . . .".format(self.name))
        i_lost = False
        election_over = False
        # send election start message
        no_message_count = 0
        self.radio.send(election_name_declare_message(self.name))
        while not election_over:
            warbot_message = self.radio.receive_message()
            if warbot_message is not None:
                if warbot_message[MESSAGE_TYPE] == WARBOT_ONLINE:
                    no_message_count = 0
                elif (warbot_message[MESSAGE_TYPE] == ELECTION_NAME_DECLARE) \
                        and warbot_message[NAME] != self.name and not i_lost:
                    logging.debug("{} received ELECTION_NAME_DECLARE message: {}".format(self.name, warbot_message))
                    no_message_count = 0
                    their_id = self.extract_id_from_warbot_name(warbot_message[NAME])
                    if self.compare_ids(their_id):  # I win the comparison
                        logging.info("{}: {} beats {}".format(self.name, self.name, warbot_message[NAME]))
                        self.radio.send(election_compare_message(self.name, warbot_message[NAME]))
                        # save the warbot's name for team assignment (assuming election win)
                        self.warbot_names.append(warbot_message[NAME])
                    else:  # they won the comparison
                        # logging.info("{}: {} loses to {}".format(self.name, self.name, warbot_message[NAME]))
                        i_lost = True
                elif warbot_message[MESSAGE_TYPE] == ELECTION_COMPARE:
                    logging.info("{}: Received ELECTION_COMPARE message: {}".format(self.name, warbot_message))
                    no_message_count = 0
                elif (warbot_message[MESSAGE_TYPE] == ELECTION_END) and i_lost:
                    logging.info("{}: Received ELECTION_END message.  Election is over.  Squad leader is {}"
                                 .format(self.name, warbot_message[WINNER_NAME]))
                    self.squad_leader = warbot_message[WINNER_NAME]
                    election_over = True
            else:
                no_message_count = no_message_count + 1
                sleep(ELECTION_SLEEP_WAIT)
            if (no_message_count > ELECTION_WINNER_WAIT_CYCLES) and not i_lost:
                # enough time has passed without a challenger, so I won
                self.radio.send(election_end_message(self.name))
                logging.info("{}: The election is over.  I am the squad leader".format(self.name))
                self.squad_leader = self.name
                election_over = True

    def get_team_assignment(self):
        if self.i_am_squad_leader():
            logging.debug("{}: Determining teams and sending team assignment message . . .".format(self.name))
            logging.debug("{}: Recorded warbot_names is {}".format(self.name, self.warbot_names))
            self.team_a_leader = self.squad_leader
            self.team_a.append(self.squad_leader)
            last_added = None
            for warbot_name in self.warbot_names:
                # make sure team_b_leader gets assigned
                if self.team_b_leader is None:
                    self.team_b_leader = warbot_name
                    self.team_b.append(warbot_name)
                    last_added = TEAM_B
                # then alternate between assigning to team_a and team_b
                elif last_added == TEAM_B:
                    self.team_a.append(warbot_name)
                    last_added = TEAM_A
                elif last_added == TEAM_A:
                    self.team_b.append(warbot_name)
                    last_added = TEAM_B
            self.radio.send(team_assignment_message(self.team_a_leader, self.team_a, self.team_b_leader, self.team_b))
            logging.debug("{}: Team assignment message sent. ".format(self.name))
        else:
            logging.debug("{}: Awaiting team assignment message . . .".format(self.name))
            team_assignment_received = False
            while not team_assignment_received:
                warbot_message = self.radio.receive_message()
                if warbot_message is not None:
                    if warbot_message[MESSAGE_TYPE] == TEAM_ASSIGNMENT:
                        self.team_a_leader = warbot_message[TEAM_A_LEADER]
                        self.team_a = warbot_message[TEAM_A]
                        self.team_b_leader = warbot_message[TEAM_B_LEADER]
                        self.team_b = warbot_message[TEAM_B]
                        logging.debug("{}: Received TEAM_ASSIGNMENT from squad leader.  I am {}"
                                      .format(self.name, self.get_role_name()))
                        team_assignment_received = True
                else:
                    logging.debug("{}: No team assignment message received.  Sleeping a bit . . .".format(self.name))
                    sleep(TEAM_ASSIGNMENT_SLEEP_WAIT)

    def handle_warbot_messages(self):
        warbot_message = self.radio.receive_message()
        while warbot_message is not None:
            logging.debug("{}: Received warbot_message: {}".format(self.name, warbot_message))
            # more handling goes here
            warbot_message = self.radio.receive_message()

    def handle_sim_messages(self, sim_messages):
        for sim_message in sim_messages:
            # logging.debug("{}: Received sim_message: {}".format(self.name, sim_message))
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
        # conduct leader election and organize teams
        self.conduct_election()
        self.get_team_assignment()
        # primary action loop
        while self.run_simulation:
            # get and handle warbot messages
            self.handle_warbot_messages()

            # get and handle simulation messages
            sim_messages = self.receive_sim_messages()
            self.handle_sim_messages(sim_messages)
        self.shutdown()

