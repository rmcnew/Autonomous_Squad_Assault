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
import numpy
from shared import WINDOW_HEIGHT, WINDOW_WIDTH, CELL_SIZE
from drawable import Drawable


class Grid:
    def __init__(self):
        self.width = int(WINDOW_WIDTH / CELL_SIZE)
        self.height = int(WINDOW_HEIGHT / CELL_SIZE)
        # create grid
        self.array = numpy.zeros((self.width, self.height), numpy.int8)

    def __getitem__(self, item):  # item must be a Point
        return Drawable(self.array[item.x][item.y])

    def __setitem__(self, key, value):  # key must be a Point, value must be a Drawable
        self.array[key.x][key.y] = value.value

    def get_dirty_counts(self):
        dirty_count = 0
        filthy_count = 0
        for x in range(0, self.width):
            for y in range(0, self.height):
                if Drawable(self.array[x][y]).name.endswith('DIRTY'):
                    dirty_count = dirty_count + 1
                elif Drawable(self.array[x][y]).name.endswith('FILTHY'):
                    filthy_count = filthy_count + 1
        return dirty_count, filthy_count

    def enter(self, location, mover):
        current = Drawable(self.array[location.x][location.y])
        if mover is Drawable.ROBOVAC_1:
            if current is Drawable.CLEAN:
                self.array[location.x][location.y] = Drawable.ROBOVAC_1.value
            elif current is Drawable.DIRTY:
                self.array[location.x][location.y] = Drawable.ROBOVAC_1_AND_DIRTY.value
            elif current is Drawable.FILTHY:
                self.array[location.x][location.y] = Drawable.ROBOVAC_1_AND_FILTHY.value

        elif mover is Drawable.ROBOVAC_2:
            if current is Drawable.CLEAN:
                self.array[location.x][location.y] = Drawable.ROBOVAC_2.value
            elif current is Drawable.DIRTY:
                self.array[location.x][location.y] = Drawable.ROBOVAC_2_AND_DIRTY.value
            elif current is Drawable.FILTHY:
                self.array[location.x][location.y] = Drawable.ROBOVAC_2_AND_FILTHY.value

        elif mover is Drawable.ROBOVAC_3:
            if current is Drawable.CLEAN:
                self.array[location.x][location.y] = Drawable.ROBOVAC_3.value
            elif current is Drawable.DIRTY:
                self.array[location.x][location.y] = Drawable.ROBOVAC_3_AND_DIRTY.value
            elif current is Drawable.FILTHY:
                self.array[location.x][location.y] = Drawable.ROBOVAC_3_AND_FILTHY.value

        elif mover is Drawable.ROBOVAC_4:
            if current is Drawable.CLEAN:
                self.array[location.x][location.y] = Drawable.ROBOVAC_4.value
            elif current is Drawable.DIRTY:
                self.array[location.x][location.y] = Drawable.ROBOVAC_4_AND_DIRTY.value
            elif current is Drawable.FILTHY:
                self.array[location.x][location.y] = Drawable.ROBOVAC_4_AND_FILTHY.value

        elif mover is Drawable.DOG_1:
            if current is Drawable.CLEAN:
                self.array[location.x][location.y] = Drawable.DOG_1.value
            elif current is Drawable.DIRTY:
                self.array[location.x][location.y] = Drawable.DOG_1_AND_DIRTY.value
            elif current is Drawable.FILTHY:
                self.array[location.x][location.y] = Drawable.DOG_1_AND_FILTHY.value

        elif mover is Drawable.DOG_2:
            if current is Drawable.CLEAN:
                self.array[location.x][location.y] = Drawable.DOG_2.value
            elif current is Drawable.DIRTY:
                self.array[location.x][location.y] = Drawable.DOG_2_AND_DIRTY.value
            elif current is Drawable.FILTHY:
                self.array[location.x][location.y] = Drawable.DOG_2_AND_FILTHY.value

        elif mover is Drawable.DOG_3:
            if current is Drawable.CLEAN:
                self.array[location.x][location.y] = Drawable.DOG_3.value
            elif current is Drawable.DIRTY:
                self.array[location.x][location.y] = Drawable.DOG_3_AND_DIRTY.value
            elif current is Drawable.FILTHY:
                self.array[location.x][location.y] = Drawable.DOG_3_AND_FILTHY.value

        elif mover is Drawable.DOG_4:
            if current is Drawable.CLEAN:
                self.array[location.x][location.y] = Drawable.DOG_4.value
            elif current is Drawable.DIRTY:
                self.array[location.x][location.y] = Drawable.DOG_4_AND_DIRTY.value
            elif current is Drawable.FILTHY:
                self.array[location.x][location.y] = Drawable.DOG_4_AND_FILTHY.value

    def exit(self, location, mover):
        current = Drawable(self.array[location.x][location.y])
        if mover is Drawable.ROBOVAC_1:
            if current is Drawable.ROBOVAC_1:
                self.array[location.x][location.y] = Drawable.CLEAN.value
            elif current is Drawable.ROBOVAC_1_AND_DIRTY:
                self.array[location.x][location.y] = Drawable.DIRTY.value
            elif current is Drawable.ROBOVAC_1_AND_FILTHY:
                self.array[location.x][location.y] = Drawable.FILTHY.value

        elif mover is Drawable.ROBOVAC_2:
            if current is Drawable.ROBOVAC_2:
                self.array[location.x][location.y] = Drawable.CLEAN.value
            elif current is Drawable.ROBOVAC_2_AND_DIRTY:
                self.array[location.x][location.y] = Drawable.DIRTY.value
            elif current is Drawable.ROBOVAC_2_AND_FILTHY:
                self.array[location.x][location.y] = Drawable.FILTHY.value

        elif mover is Drawable.ROBOVAC_3:
            if current is Drawable.ROBOVAC_3:
                self.array[location.x][location.y] = Drawable.CLEAN.value
            elif current is Drawable.ROBOVAC_3_AND_DIRTY:
                self.array[location.x][location.y] = Drawable.DIRTY.value
            elif current is Drawable.ROBOVAC_3_AND_FILTHY:
                self.array[location.x][location.y] = Drawable.FILTHY.value

        elif mover is Drawable.ROBOVAC_4:
            if current is Drawable.ROBOVAC_4:
                self.array[location.x][location.y] = Drawable.CLEAN.value
            elif current is Drawable.ROBOVAC_4_AND_DIRTY:
                self.array[location.x][location.y] = Drawable.DIRTY.value
            elif current is Drawable.ROBOVAC_4_AND_FILTHY:
                self.array[location.x][location.y] = Drawable.FILTHY.value

        elif mover is Drawable.DOG_1:
            if current is Drawable.DOG_1:
                self.array[location.x][location.y] = Drawable.CLEAN.value
            elif current is Drawable.DOG_1_AND_DIRTY:
                self.array[location.x][location.y] = Drawable.DIRTY.value
            elif current is Drawable.DOG_1_AND_FILTHY:
                self.array[location.x][location.y] = Drawable.FILTHY.value

        elif mover is Drawable.DOG_2:
            if current is Drawable.DOG_2:
                self.array[location.x][location.y] = Drawable.CLEAN.value
            elif current is Drawable.DOG_2_AND_DIRTY:
                self.array[location.x][location.y] = Drawable.DIRTY.value
            elif current is Drawable.DOG_2_AND_FILTHY:
                self.array[location.x][location.y] = Drawable.FILTHY.value

        elif mover is Drawable.DOG_3:
            if current is Drawable.DOG_3:
                self.array[location.x][location.y] = Drawable.CLEAN.value
            elif current is Drawable.DOG_3_AND_DIRTY:
                self.array[location.x][location.y] = Drawable.DIRTY.value
            elif current is Drawable.DOG_3_AND_FILTHY:
                self.array[location.x][location.y] = Drawable.FILTHY.value

        elif mover is Drawable.DOG_4:
            if current is Drawable.DOG_4:
                self.array[location.x][location.y] = Drawable.CLEAN.value
            elif current is Drawable.DOG_4_AND_DIRTY:
                self.array[location.x][location.y] = Drawable.DIRTY.value
            elif current is Drawable.DOG_4_AND_FILTHY:
                self.array[location.x][location.y] = Drawable.FILTHY.value
