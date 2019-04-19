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

# shared functions
import datetime
import socket
import tempfile


def get_ip_address():
    temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        temp_socket.connect(('192.0.0.8', 1027))
    except socket.error:
        return None
    return temp_socket.getsockname()[0]


def timestamp():
    return datetime.datetime.now().isoformat()


def get_elapsed_time(start_time):
    current_time = datetime.datetime.now()
    elapsed_time = current_time - start_time
    return elapsed_time


def get_temp_dir():
    return tempfile.mkdtemp()


def is_odd(num):
    return num % 2 == 1


def is_even(num):
    return num % 2 == 0


