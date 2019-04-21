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
from shared.functions import distance
from simulation import a_star
from simulation.direction import Direction
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
        self.ready_to_flank = set()
        self.limit_of_advance_attained = set()
        self.security_established = set()
        self.moving = False
        self.firing = False
        self.fire_direction = None
        self.flanking_position = None
        self.flanking_position_reached = False
        self.flanking_position_waypoint = None
        self.flanking_position_waypoint_reached = False
        self.limit_of_advance = None
        self.limit_of_advance_reached = False
        self.objective_clearance_direction = None
        self.last_objective_clearance_action = MOVE
        self.secure_objective_location = None
        self.secure_objective_location_route_planned = False

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

    def calculate_traveling_team_column_wedge_position(self, team_leader_waypoint):
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
        return team_leader_waypoint.plus_vector(offset)

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
        if self.opfor_visible():
            logging.debug("{}: OPFOR sighted.  Notifying squad . . .")
            self.radio.send(opfor_contact_message())
            self.team_state = OPFOR_CONTACT
        if not self.moving:
            if self.i_am_squad_leader():
                # is objective on visible map
                if self.visible_map.objective_location is not None:  # path find to objective
                    self.movement_target = Point(self.objective_location.x,
                                           self.objective_location.y + WARBOT_VISION_DISTANCE - 2)
                    logging.debug("{}: Objective is on visible map at location: {}.  "
                                  "Starting A* path finding from {} to {}"
                                  .format(self.name, self.visible_map.objective_location,
                                          self.location, self.movement_target))
                    self.path = a_star.find_path(self.visible_map, self.location, self.movement_target)
                else:  # else move in general direction
                    logging.debug("{}: Objective is NOT on visible map.  Moving in general direction".format(self.name))
                    next_waypoint = self.visible_map.find_closest_top_point(Point(self.objective_location.x,
                                           self.objective_location.y + WARBOT_VISION_DISTANCE - 2))
                    logging.debug("{}: Calculated next_waypoint is: {}".format(self.name, next_waypoint))
                    self.movement_target = next_waypoint
                    self.path = a_star.find_path(self.visible_map, self.location, self.movement_target)
                    logging.debug("{}: A* path to next_waypoint is: {}".format(self.name, self.path))
                    self.radio.send(squad_leader_waypoint_message(next_waypoint))
            else:  # I am not the squad leader
                # is objective on visible map
                if self.visible_map.objective_location is not None:  # path find to objective
                    self.movement_target = self.objective_location
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
                        elif warbot_message[MESSAGE_TYPE] == OPFOR_CONTACT:
                            self.team_state = OPFOR_CONTACT
                    else:
                        sleep(0.3)
        else:
            sleep(0.3)

    def get_suppressive_fire_position_offset(self, suppressive_fire_position):
        team_index = self.get_team_index()
        offset = None
        if team_index == 1:
            offset = SUPPRESSIVE_A1_OFFSET
        elif team_index == 2:
            offset = SUPPRESSIVE_A2_OFFSET
        elif team_index == 3:
            offset = SUPPRESSIVE_A3_OFFSET
        elif team_index == 4:
            offset = SUPPRESSIVE_A4_OFFSET
        return suppressive_fire_position.plus_vector(offset)

    def get_flanking_position_offset(self, flanking_position):
        team_index = self.get_team_index()
        offset = None
        if team_index == 1:
            offset = FLANKING_B1_OFFSET
        elif team_index == 2:
            offset = FLANKING_B2_OFFSET
        elif team_index == 3:
            offset = FLANKING_B3_OFFSET
        elif team_index == 4:
            offset = FLANKING_B4_OFFSET
        return flanking_position.plus_vector(offset)

    def react_to_contact_team_a(self):
        if self.i_am_squad_leader() and self.flanking_position is None:  # squad leader halts and aligns
            logging.debug("{}: Squad leader aligning with objective".format(self.name))
            self.flanking_position = Point(self.objective_location.x,
                                           self.objective_location.y + WARBOT_VISION_DISTANCE - 2)
            self.movement_target = self.flanking_position
            logging.debug("{}: Notifying Team A of suppressive fire position: {}"
                          .format(self.name, self.flanking_position))
            self.radio.send(suppressive_fire_position_message(self.flanking_position))
            self.path = a_star.find_path(self.visible_map, self.location, self.movement_target)
        elif self.i_am_squad_leader() and self.flanking_position == self.location:
            # receive / accumulate messages from Team B until they are all ready to flank
            warbot_message = self.radio.receive_message()
            if warbot_message is not None:
                if warbot_message[MESSAGE_TYPE] == READY_TO_FLANK:
                    logging.debug("{}: Received READY_TO_FLANK from {}".format(self.name, warbot_message[NAME]))
                    self.ready_to_flank.add(warbot_message[NAME])
                    if len(self.ready_to_flank) == len(self.team_b):
                        logging.debug("Team B is READY_TO_FLANK.")
                        self.radio.send(lift_and_shift_fire_message())
                        self.team_state = LIFT_AND_SHIFT_FIRE
            # direct suppressive fire for Team A
            logging.debug("{}: Directing suppressive fire".format(self.name))
            self.fire_direction = Direction.NORTH
            sleep(0.5)
        elif self.i_am_squad_leader() and self.flanking_position is not None:  # get aligned with objective
            logging.debug("{}: Getting aligned with objective")
            sleep(0.5)
        elif not self.i_am_squad_leader() and self.flanking_position is None:
            warbot_message = self.radio.receive_message()
            if warbot_message is not None:
                if warbot_message[MESSAGE_TYPE] == SUPPRESSIVE_FIRE_POSITION:
                    self.flanking_position = self.get_suppressive_fire_position_offset(
                        Point.from_dict(warbot_message[LOCATION]))
                    self.movement_target = self.flanking_position
                    logging.debug("{}: suppressive fire position is: {}".format(self.name, self.movement_target))
                    self.path = a_star.find_path(self.visible_map, self.location, self.movement_target)
                    logging.debug("{}: A* path to suppressive fire position is: {}".format(self.name, self.path))
            else:
                sleep(0.3)
        elif not self.i_am_squad_leader() and self.location == self.flanking_position:
            logging.debug("{}: Suppressive fire".format(self.name))
            self.fire_direction = Direction.NORTH
            warbot_message = self.radio.receive_message()
            if warbot_message is not None:
                if warbot_message[MESSAGE_TYPE] == LIFT_AND_SHIFT_FIRE:
                    logging.debug("{}: LIFT_AND_SHIFT_FIRE signal received".format(self.name))
                    self.team_state = LIFT_AND_SHIFT_FIRE
            sleep(0.3)
        else:
            sleep(0.3)

    def react_to_contact_team_b(self):
        # determine flanking position base and flanking position waypoint; send to team B
        if self.i_am_team_b_leader() and self.flanking_position is None:
            logging.debug("{}: Establishing Team B flanking position and waypoint".format(self.name))
            self.flanking_position, self.flanking_position_waypoint = self.visible_map.find_flanking_waypoint(
                self.objective_location, self.location)
            logging.debug("{}: Flanking position is: {}.  "
                          "Flanking position waypoint is {}.  Notifying Team B . . ."
                          .format(self.name, self.flanking_position, self.flanking_position_waypoint))
            # send team the waypoint
            self.radio.send(flanking_position_message(self.flanking_position_waypoint, self.flanking_position))

        # get flanking position and flanking position waypoint from Team B Leader
        elif not self.i_am_team_b_leader() and self.flanking_position is None:
            warbot_message = self.radio.receive_message()
            if warbot_message is not None:
                if warbot_message[MESSAGE_TYPE] == FLANKING_POSITION:
                    logging.debug("{}: received flanking position message from Team B Leader"
                                  .format(self.name))
                    self.flanking_position_waypoint = self.calculate_traveling_team_column_wedge_position(
                        Point.from_dict(warbot_message[FLANKING_POSITION_WAYPOINT]))
                    self.flanking_position = self.get_flanking_position_offset(Point.from_dict(
                        warbot_message[FLANKING_POSITION]))

        # move to flanking position waypoint and then flanking position
        elif self.flanking_position is not None:
            if not self.flanking_position_waypoint_reached:
                if self.flanking_position_waypoint == self.location:
                    logging.debug("{}: Reached flanking position waypoint: {}"
                                  .format(self.name, self.flanking_position_waypoint))
                    self.flanking_position_waypoint_reached = True
                else:
                    if self.visible_map.is_left_of_me(self.flanking_position_waypoint, self.location):
                        self.movement_target = self.visible_map.find_closest_left_point(
                            self.flanking_position_waypoint)
                    else:  # flanking_position_waypoint is to the right
                        self.movement_target = self.visible_map.find_closest_right_point(
                            self.flanking_position_waypoint)
                    logging.debug("{}: Finding path to flanking position waypoint: {}"
                                  .format(self.name, self.movement_target))
                    self.path = a_star.find_path(self.visible_map, self.location, self.movement_target)
                    logging.debug("{}: A* path to waypoint is: {}".format(self.name, self.path))

            elif self.flanking_position_waypoint_reached and not self.flanking_position_reached:
                if self.flanking_position == self.location:
                    logging.debug("{}: Reached flanking position: {}"
                                  .format(self.name, self.flanking_position))
                    self.flanking_position_reached = True
                else:
                    self.movement_target = self.visible_map.find_closest_top_point(self.flanking_position)
                    logging.debug("{}: Finding path to flanking position: {}"
                                  .format(self.name, self.movement_target))
                    self.path = a_star.find_path(self.visible_map, self.location, self.movement_target)
                    logging.debug("{}: A* path to waypoint is: {}".format(self.name, self.path))

            elif self.flanking_position_reached:
                if len(self.ready_to_flank) == 0:
                    logging.debug("{}: Sending READY_TO_FLANK to squad leader".format(self.name))
                    self.ready_to_flank.add(self.name)
                    self.radio.send(ready_to_flank_message(self.name))
                    sleep(0.3)
                warbot_message = self.radio.receive_message()
                if warbot_message is not None:
                    if warbot_message[MESSAGE_TYPE] == LIFT_AND_SHIFT_FIRE:
                        logging.debug("{}: LIFT_AND_SHIFT_FIRE signal received".format(self.name))
                        self.team_state = LIFT_AND_SHIFT_FIRE
            else:  # flanking waypoint reached, go to flanking position
                logging.error("{}: Should not reach here!".format(self.name))
                sleep(0.5)

    def react_to_contact(self):
        if not self.moving:
            if self.i_am_on_team_a():  # team_a moves into a line formation and begins suppressive fire against OPFOR
                self.react_to_contact_team_a()

            else:  # team_b moves to a flanking position and then notifies squad leader
                self.react_to_contact_team_b()
        else:
            sleep(0.3)

    def lift_and_shift_fire_team_a(self):
        self.fire_direction = None
        if self.i_am_squad_leader():
            warbot_message = self.radio.receive_message()
            if warbot_message is not None:
                if warbot_message[MESSAGE_TYPE] == LIMIT_OF_ADVANCE:
                    self.limit_of_advance_attained.add(warbot_message[NAME])
                    # after all Team B reaches limit of advance, secure the objective
                    if len(self.limit_of_advance_attained) == len(self.team_b):
                        self.radio.send(secure_objective_message())
                        self.fire_direction = None
                        self.team_state = SECURE_OBJECTIVE
            else:
                sleep(0.5)
        else:
            warbot_message = self.radio.receive_message()
            if warbot_message is not None:
                if warbot_message[MESSAGE_TYPE] == SECURE_OBJECTIVE:
                    self.fire_direction = None
                    self.team_state = SECURE_OBJECTIVE
            else:
                sleep(0.5)

    def lift_and_shift_fire_team_b(self):
        if self.limit_of_advance is None:
            half_limit_of_advance = distance(self.visible_map.warbot_locations[self.team_b_leader],
                                             self.objective_location)
            if self.visible_map.is_left_of_me(self.objective_location, self.location):
                advance_vector = Direction.WEST.to_scaled_vector(2 * half_limit_of_advance)
                self.limit_of_advance = self.location.plus_vector(advance_vector)
                self.objective_clearance_direction = Direction.WEST
                logging.debug("{}: limit_of_advance is: {}, objective_clearance_direction is: {}"
                              .format(self.name, self.limit_of_advance, self.objective_clearance_direction))
            else:  # objective is to the right
                advance_vector = Direction.EAST.to_scaled_vector(2 * half_limit_of_advance)
                self.limit_of_advance = self.location.plus_vector(advance_vector)
                self.objective_clearance_direction = Direction.EAST
                logging.debug("{}: limit_of_advance is: {}, objective_clearance_direction is: {}"
                              .format(self.name, self.limit_of_advance, self.objective_clearance_direction))
            sleep(0.3)
        elif not self.limit_of_advance_reached:
            if self.last_objective_clearance_action == MOVE:
                self.fire_direction = self.objective_clearance_direction
                self.last_objective_clearance_action = SHOOT
            else:
                self.fire_direction = None
                next_step = self.location.plus_direction(self.objective_clearance_direction)
                self.path.append(next_step)
                self.last_objective_clearance_action = MOVE
                if next_step == self.limit_of_advance:
                    self.radio.send(limit_of_advance_message(self.name))
                    self.limit_of_advance_reached = True
            sleep(0.2)
        else:  # wait for squad leader to call "secure objective"
            warbot_message = self.radio.receive_message()
            if warbot_message is not None:
                if warbot_message[MESSAGE_TYPE] == SECURE_OBJECTIVE:
                    self.fire_direction = None
                    self.team_state = SECURE_OBJECTIVE
            else:
                sleep(0.3)

    def lift_and_shift_fire(self):
        # logging.debug("{}: Lifting and shifting fire".format(self.name))
        if not self.moving:
            if self.i_am_on_team_a():  # team_a stops firing as team_b sweeps across the objective
                self.lift_and_shift_fire_team_a()

            else:  # team_b fires and sweeps across the objective
                self.lift_and_shift_fire_team_b()
        else:
            sleep(0.3)

    def secure_objective(self):
        if not self.moving:
            # calculate the security perimeter position
            if self.secure_objective_location is None:
                warbot_id = self.extract_id_from_warbot_name(self.name)
                offset = None
                if warbot_id == 1:
                    offset = SECURITY_PERIMETER_1_OFFSET
                elif warbot_id == 2:
                    offset = SECURITY_PERIMETER_2_OFFSET
                elif warbot_id == 3:
                    offset = SECURITY_PERIMETER_3_OFFSET
                elif warbot_id == 4:
                    offset = SECURITY_PERIMETER_4_OFFSET
                elif warbot_id == 5:
                    offset = SECURITY_PERIMETER_5_OFFSET
                elif warbot_id == 6:
                    offset = SECURITY_PERIMETER_6_OFFSET
                elif warbot_id == 7:
                    offset = SECURITY_PERIMETER_7_OFFSET
                elif warbot_id == 8:
                    offset = SECURITY_PERIMETER_8_OFFSET
                elif warbot_id == 9:
                    offset = SECURITY_PERIMETER_9_OFFSET
                elif warbot_id == 10:
                    offset = SECURITY_PERIMETER_10_OFFSET
                else:
                    logging.error("Should not get here!")
                self.secure_objective_location = self.objective_location.plus_vector(offset)
                logging.debug("{}: secure_objective_location is: {}".format(self.name, self.secure_objective_location))
                sleep(0.2)
            # if we know where we are supposed to go, but cannot see it, go in the general direction until we can see it
            elif self.secure_objective_location is not None and not (self.visible_map.on_map(
                    self.secure_objective_location) and len(self.path) == 0):
                if self.visible_map.is_left_of_me(self.secure_objective_location, self.location):
                    self.movement_target = self.visible_map.find_closest_left_point(
                        self.secure_objective_location)
                else:  # secure_objective_location is to the right
                    self.movement_target = self.visible_map.find_closest_right_point(
                        self.secure_objective_location)
                logging.debug("{}: Finding path in direction of secure_objective_location : {}"
                              .format(self.name, self.movement_target))
                self.path = a_star.find_path(self.visible_map, self.location, self.movement_target)
                logging.debug("{}: A* path towards secure_objective_location is: {}".format(self.name, self.path))
            # if we know where we are supposed to go and can see it, find the path
            elif self.secure_objective_location is not None and \
                    (self.visible_map.on_map(self.secure_objective_location)) and \
                    not self.secure_objective_location_route_planned:
                self.movement_target = self.secure_objective_location
                logging.debug("{}: Finding path to security perimeter position: {}"
                              .format(self.name, self.movement_target))
                self.path = a_star.find_path(self.visible_map, self.location, self.movement_target)
                logging.debug("{}: A* path to security perimeter position is: {}".format(self.name, self.path))
                self.secure_objective_location_route_planned = True
                sleep(0.2)
            # route planned to security perimeter position, just travel there
            elif self.secure_objective_location is not None and \
                    self.secure_objective_location_route_planned and self.location != self.secure_objective_location:
                logging.debug("{}: Moving to security perimeter position: {}"
                              .format(self.name, self.secure_objective_location))
                sleep(0.5)
            # after in security perimeter position, let squad leader know
            elif self.secure_objective_location is not None and self.location == self.secure_objective_location:
                if not self.i_am_squad_leader() and len(self.security_established) == 0:
                    self.radio.send(in_security_perimeter_position_message(self.name))
                    self.security_established.add(self.name)
                    sleep(0.5)
                elif self.i_am_squad_leader():  # if squad leader, ensure security perimeter is established
                    warbot_message = self.radio.receive_message()
                    if warbot_message is not None:
                        if warbot_message[MESSAGE_TYPE] == IN_SECURITY_PERIMETER_POSITION:
                            self.security_established.add(warbot_message[NAME])
                            if len(self.security_established) == len(self.warbot_names):
                                self.put_sim_message(mission_complete_message())
                    else:
                        sleep(0.5)
                else:
                    sleep(0.5)

    def do_warbot_tasks(self):
        if self.team_state == CONDUCT_ELECTION:
            self.conduct_election()

        elif self.team_state == GET_TEAM_ASSIGNMENT:
            self.get_team_assignment()

        elif self.team_state == FORM_SQUAD_COLUMN_WEDGE:
            self.form_squad_column_wedge()

        elif self.team_state == MOVEMENT_TO_OBJECTIVE:
            self.movement_to_objective()

        elif self.team_state == OPFOR_CONTACT:
            self.react_to_contact()

        elif self.team_state == LIFT_AND_SHIFT_FIRE:
            self.lift_and_shift_fire()

        elif self.team_state == SECURE_OBJECTIVE:
            self.secure_objective()

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

        elif self.team_state == OPFOR_CONTACT:
            if len(self.path) > 0:
                self.moving = True
                return take_turn_move_message(self.name, self.path.pop(0))
            elif self.fire_direction is not None:
                self.firing = True
                return take_turn_fire_message(self.name, self.location, self.fire_direction)
            else:
                return take_turn_do_nothing_message(self.name)

        elif self.team_state == LIFT_AND_SHIFT_FIRE:
            if len(self.path) > 0:
                self.moving = True
                return take_turn_move_message(self.name, self.path.pop(0))
            elif self.fire_direction is not None:
                self.firing = True
                return take_turn_fire_message(self.name, self.location, self.fire_direction)
            else:
                return take_turn_do_nothing_message(self.name)

        elif self.team_state == SECURE_OBJECTIVE:
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
                if self.firing:
                    self.firing = False
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

