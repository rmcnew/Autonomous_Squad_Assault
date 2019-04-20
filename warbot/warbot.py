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
from simulation import a_star
from simulation.point import Point
from warbot.warbot_messages import *
from warbot.warbot_radio import WarbotRadio


class Warbot(Agent):
    """Represents an autonomous robotic warrior"""
    def __init__(self, to_me_queue, from_me_queue, initial_location, initial_visible_map, name,
                 to_this_warbot_queue, warbot_radio_broker, objective_location, rally_point_location):
        Agent.__init__(self, to_me_queue, from_me_queue, initial_location,
                       initial_visible_map, WARBOT_VISION_DISTANCE, name)
        self.radio = WarbotRadio(self.name, to_this_warbot_queue, warbot_radio_broker)
        self.path = []
        self.objective_location = objective_location
        self.rally_point_location = rally_point_location
        self.run_simulation = True
        self.warbot_names = []
        self.squad_leader = None  # squad leader is also team_a leader
        self.team_a = []
        self.team_b_leader = None
        self.team_b = []
        self.team_state = CONDUCT_ELECTION
        self.movement_target = None
        self.ready_for_movement = set()
        self.moving = False

    def i_am_squad_leader(self):
        return self.squad_leader is not None and self.squad_leader == self.name

    def i_am_team_b_leader(self):
        return self.team_b_leader is not None and self.team_b_leader == self.name

    def i_am_on_team_a(self):
        return self.name in self.team_a

    def i_am_on_team_b(self):
        return self.name in self.team_b

    def get_role_name(self):
        if self.i_am_squad_leader():
            return "{} . My team is: {}".format(SQUAD_LEADER, self.team_a)
        elif self.i_am_team_b_leader():
            return "{} . My team is: {}".format(TEAM_B_LEADER, self.team_b)
        elif self.i_am_on_team_a():
            return ON_TEAM_A
        elif self.i_am_on_team_b():
            return ON_TEAM_B

    def get_team_index(self):
        if self.i_am_on_team_a():
            return self.team_a.index(self.name)
        else:
            return self.team_b.index(self.name)

    def opfor_visible(self):
        return len(self.visible_map.opfor_locations) > 0

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
                    self.team_state = GET_TEAM_ASSIGNMENT
                    election_over = True
            else:
                no_message_count = no_message_count + 1
                sleep(ELECTION_SLEEP_WAIT)
            if (no_message_count > ELECTION_WINNER_WAIT_CYCLES) and not i_lost:
                # enough time has passed without a challenger, so I won
                self.radio.send(election_end_message(self.name))
                logging.info("{}: The election is over.  I am the squad leader".format(self.name))
                self.squad_leader = self.name
                self.team_state = GET_TEAM_ASSIGNMENT
                election_over = True

    def get_team_assignment(self):
        if self.i_am_squad_leader():
            logging.debug("{}: Determining teams and sending team assignment message . . .".format(self.name))
            logging.debug("{}: Recorded warbot_names is {}".format(self.name, self.warbot_names))
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
            self.radio.send(team_assignment_message(self.squad_leader, self.team_a, self.team_b_leader, self.team_b))
            logging.debug("{}: Team assignment message sent.  I am {}".format(self.name, self.get_role_name()))
            self.team_state = FORM_SQUAD_COLUMN_WEDGE
        else:
            logging.debug("{}: Awaiting team assignment message . . .".format(self.name))
            team_assignment_received = False
            while not team_assignment_received:
                warbot_message = self.radio.receive_message()
                if warbot_message is not None:
                    if warbot_message[MESSAGE_TYPE] == TEAM_ASSIGNMENT:
                        self.squad_leader = warbot_message[SQUAD_LEADER]
                        self.team_a = warbot_message[TEAM_A]
                        self.team_b_leader = warbot_message[TEAM_B_LEADER]
                        self.team_b = warbot_message[TEAM_B]
                        logging.debug("{}: Received TEAM_ASSIGNMENT from squad leader.  I am {}"
                                      .format(self.name, self.get_role_name()))
                        team_assignment_received = True
                        self.team_state = FORM_SQUAD_COLUMN_WEDGE
                else:
                    logging.debug("{}: No team assignment message received.  Sleeping a bit . . .".format(self.name))
                    sleep(TEAM_ASSIGNMENT_SLEEP_WAIT)

    def calculate_traveling_squad_column_wedge_position(self, squad_leader_waypoint):
        # logging.debug("calculate_traveling_squad_column_wedge_position: visible_map.warbot_locations is {}"
        #               .format(self.visible_map.warbot_locations))
        if self.i_am_team_b_leader():
            return squad_leader_waypoint.plus_vector(SCW_TEAM_B_LEADER_OFFSET)
        elif self.i_am_on_team_a():  # team_a starts on left
            team_index = self.get_team_index()
            offset = None
            if team_index == 1:
                offset = SCW_A1_OFFSET
            elif team_index == 2:
                offset = SCW_A2_OFFSET
            elif team_index == 3:
                offset = SCW_A3_OFFSET
            elif team_index == 4:
                offset = SCW_A4_OFFSET
            return squad_leader_waypoint.plus_vector(offset)
        elif self.i_am_on_team_b():  # team_b starts on right
            offset = None
            team_index = self.get_team_index()
            if team_index == 1:
                offset = SCW_B1_OFFSET
            elif team_index == 2:
                offset = SCW_B2_OFFSET
            elif team_index == 3:
                offset = SCW_B3_OFFSET
            elif team_index == 4:
                offset = SCW_B4_OFFSET
            return squad_leader_waypoint.plus_vector(SCW_TEAM_B_LEADER_OFFSET).plus_vector(offset)

    def calculate_rally_point_squad_column_wedge_position(self):
        # logging.debug("calculate_squad_column_wedge_position: visible_map.warbot_locations is {}"
        #               .format(self.visible_map.warbot_locations))
        squad_leader_position = self.rally_point_location.plus_vector(SCW_SQUAD_LEADER_OFFSET)
        if self.i_am_squad_leader():
            return squad_leader_position
        elif self.i_am_team_b_leader():
            return squad_leader_position.plus_vector(SCW_TEAM_B_LEADER_OFFSET)
        elif self.i_am_on_team_a():  # team_a starts on left
            team_index = self.get_team_index()
            offset = None
            if team_index == 1:
                offset = SCW_A1_OFFSET
            elif team_index == 2:
                offset = SCW_A2_OFFSET
            elif team_index == 3:
                offset = SCW_A3_OFFSET
            elif team_index == 4:
                offset = SCW_A4_OFFSET
            return squad_leader_position.plus_vector(offset)
        elif self.i_am_on_team_b():  # team_b starts on right
            offset = None
            team_index = self.get_team_index()
            if team_index == 1:
                offset = SCW_B1_OFFSET
            elif team_index == 2:
                offset = SCW_B2_OFFSET
            elif team_index == 3:
                offset = SCW_B3_OFFSET
            elif team_index == 4:
                offset = SCW_B4_OFFSET
            return squad_leader_position.plus_vector(SCW_TEAM_B_LEADER_OFFSET).plus_vector(offset)

    def form_squad_column_wedge(self):
        if self.movement_target is None:
            logging.debug("{}: Determining position in squad column wedge . . .".format(self.name))
            self.movement_target = self.calculate_rally_point_squad_column_wedge_position()
            logging.debug("{}: My squad column wedge position is: {}.  Starting A* path finding from {} to {}"
                          .format(self.name, self.movement_target, self.location, self.movement_target))
            self.path = a_star.find_path(self.visible_map, self.location, self.movement_target)
            logging.debug("{}: Found A* path from {} to {} as {}"
                          .format(self.name, self.location, self.movement_target, self.path))
        elif self.location != self.movement_target:
            logging.debug("{}: En route from current location {} to squad column wedge location: {}"
                          .format(self.name, self.location, self.movement_target))
            if not self.moving:
                # if we are almost to movement_target, and have submitted our move, path could be empty
                if len(self.path) > 1:
                    if self.visible_map.can_enter(self.path[0]):
                        logging.debug("{}: Next location {} is clear. Moving from {} to {}"
                                      .format(self.name, self.path[0], self.location, self.path[0]))
                        sleep(0.3)
                    else:
                        logging.debug("{}: Next location {} is blocked.  Replanning route from {} to {}"
                                      .format(self.name, self.path[0], self.location, self.movement_target))
                        self.path = a_star.find_path(self.visible_map, self.location, self.movement_target)
                        logging.debug("{}: Found en route A* path from {} to {} as {}"
                                      .format(self.name, self.location, self.movement_target, self.path))
                else:  # if the path is empty, just wait
                    sleep(0.3)
            else:
                sleep(0.3)
        elif self.location == self.movement_target:
            if self.i_am_squad_leader():
                logging.debug("{} in squad column wedge position. Waiting for each warbot to notify ready."
                              .format(self.name))
                warbot_message = self.radio.receive_message()
                while warbot_message is not None:
                    if warbot_message[MESSAGE_TYPE] == READY_FOR_MOVEMENT:
                        logging.debug("{}: Received READY_FOR_MOVEMENT message from {}. "
                                      "Total ready messages received: {}"
                                      .format(self.name, warbot_message[FROM], len(self.ready_for_movement)))
                        self.ready_for_movement.add(warbot_message[FROM])
                        if len(self.ready_for_movement) == len(self.warbot_names):
                            self.radio.send(start_movement_message())
                            self.team_state = MOVEMENT_TO_OBJECTIVE
                    warbot_message = self.radio.receive_message()
            else: # I am not the squad leader
                if len(self.ready_for_movement) == 0:  # only send one notification to squad_leader
                    logging.debug("{} in squad column wedge position.  Notifying squad leader".format(self.name))
                    self.radio.send(ready_for_movement_message(self.name))
                    self.ready_for_movement.add(self.name)
                else:
                    logging.debug("{} in squad column wedge position. Squad leader previously notified."
                                  .format(self.name))
                    warbot_message = self.radio.receive_message()
                    if warbot_message is not None:
                        if warbot_message[MESSAGE_TYPE] == START_MOVEMENT:
                            self.team_state = MOVEMENT_TO_OBJECTIVE

    def movement_to_objective(self):
        # logging.debug("{}: Begin movement to objective . . .".format(self.name))
        if not self.moving:
            if self.i_am_squad_leader():
                # is objective on visible map
                if self.visible_map.objective_location is not None:  # path find to objective
                    self.movement_target = self.visible_map.objective_location
                    logging.debug("{}: Objective is on visible map at location: {}.  "
                                  "Starting A* path finding from {} to {}"
                                  .format(self.name, self.visible_map.objective_location,
                                          self.location, self.movement_target))
                    self.path = a_star.find_path(self.visible_map, self.location, self.movement_target)
                else:  # else move in general direction
                    logging.debug("{}: Objective is NOT on visible map.  Moving in general direction".format(self.name))
                    next_waypoint = self.visible_map.find_closest_top_point(self.objective_location)
                    logging.debug("{}: Calculated next_waypoint is: {}".format(self.name, next_waypoint))
                    self.movement_target = next_waypoint
                    self.path = a_star.find_path(self.visible_map, self.location, self.movement_target)
                    logging.debug("{}: A* path to next_waypoint is: {}".format(self.name, self.path))
                    self.radio.send(squad_leader_waypoint_message(next_waypoint))
            else:  # I am not the squad leader
                # is objective on visible map
                if self.visible_map.objective_location is not None:  # path find to objective
                    self.movement_target = self.visible_map.objective_location
                    logging.debug("{}: Objective is on visible map at location: {}.  "
                                  "Starting A* path finding from {} to {}"
                                  .format(self.name, self.visible_map.objective_location,
                                          self.location, self.movement_target))
                    self.path = a_star.find_path(self.visible_map, self.location, self.movement_target)
                else:  # follow the squad leader's waypoints
                    logging.debug("{}: Following squad leader in traveling squad column wedge".format(self.name))
                    warbot_message = self.radio.receive_message()
                    if warbot_message is not None:
                        if warbot_message[MESSAGE_TYPE] == SQUAD_LEADER_WAYPOINT:
                            waypoint = Point.from_dict(warbot_message[WAYPOINT])
                            self.movement_target = self.calculate_traveling_squad_column_wedge_position(waypoint)
                            logging.debug("{}: Movement target is: {}".format(self.name, self.movement_target))
                            self.path = a_star.find_path(self.visible_map, self.location, self.movement_target)
                            logging.debug("{}: A* path to movement target is: {}".format(self.name, self.path))
                    else:
                        sleep(0.3)
        else:
            sleep(0.3)

    def do_warbot_tasks(self):
        if self.team_state == CONDUCT_ELECTION:
            self.conduct_election()
        elif self.team_state == GET_TEAM_ASSIGNMENT:
            self.get_team_assignment()
        elif self.team_state == FORM_SQUAD_COLUMN_WEDGE:
            self.form_squad_column_wedge()
        elif self.team_state == MOVEMENT_TO_OBJECTIVE:
            self.movement_to_objective()
        else:
            logging.error("do_warbot_tasks: {}: Should not get here!  Bad team state: {}"
                          .format(self.name, self.team_state))

    def determine_turn_action(self):
        if self.team_state == CONDUCT_ELECTION:
            return take_turn_do_nothing_message(self.name)
        elif self.team_state == GET_TEAM_ASSIGNMENT:
            return take_turn_do_nothing_message(self.name)
        elif self.team_state == FORM_SQUAD_COLUMN_WEDGE:
            if len(self.path) > 0:
                self.moving = True
                return take_turn_move_message(self.name, self.path.pop(0))
            else:
                return take_turn_do_nothing_message(self.name)
        elif self.team_state == MOVEMENT_TO_OBJECTIVE:
            if len(self.path) > 0:
                self.moving = True
                return take_turn_move_message(self.name, self.path.pop(0))
            else:
                return take_turn_do_nothing_message(self.name)
        else:
            logging.error("determine_turn_action: {}: Should not get here! Bad team state: {} "
                          .format(self.name, self.team_state))

    def do_sim_tasks(self):
        sim_message = self.receive_sim_message()
        if sim_message is not None:
            # logging.debug("{}: Received sim_message: {}".format(self.name, sim_message))
            if sim_message[MESSAGE_TYPE] == SHUTDOWN:
                logging.debug("{} received shutdown message".format(self.name))
                self.run_simulation = False
            elif sim_message[MESSAGE_TYPE] == YOUR_TURN:
                self.update_location_and_visible_map(sim_message[VISIBLE_MAP])
                self.visible_map.scan()
                if self.moving:
                    self.moving = False
                turn_action = self.determine_turn_action()
                # logging.debug("{}: I see {} warbots nearby".format(self.name, len(self.visible_map.warbot_locations)))
                logging.debug("{} taking action: {}".format(self.name, turn_action))
                self.put_sim_message(turn_action)

    def run(self):
        # notify other warbots that this warbot is operational
        self.radio.send(warbot_online_message(self.name))
        # primary action loop
        while self.run_simulation:
            # get and handle warbot messages
            self.do_warbot_tasks()
            # get and handle simulation messages
            self.do_sim_tasks()
            sleep(0.5)
        self.shutdown()

