# -*- coding: utf-8 -*-
"""
Defines the mobs that inhabit planet Wa-Tor.
"""

import random

from abc import ABC, abstractmethod

from PySide6.QtGui import QPixmap
from PySide6.QtCore import QPoint


class MobBase(ABC):
    """
    Base class describing a world object.
    """

    def __init__(self, name, pixmap, breed=0, lastupdate=-1):
        self._name = name
        self._pixmap = pixmap
        self._breed = breed
        self._age = 0
        self._last_update = lastupdate

    @property
    def name(self):
        """
        A string name description of the world object.
        """
        return self._name

    @property
    def pixmap(self):
        """
        A pixmap representing the world object.
        """
        return self._pixmap

    @staticmethod
    def generate_move_list(pos, world):
        """
        Returns a list of potential moves to try out from a position in the world.
        """
        moves = list()
        for y in (-1, 0, 1):
            posy = pos.y() + y
            if posy < 0:
                posy += world.size.height()
            elif posy >= world.size.height():
                posy -= world.size.height()
            for x in (-1, 0, 1):
                if y == 0 and x == 0:
                    continue
                posx = pos.x() + x
                if posx < 0:
                    posx += world.size.width()
                elif posx >= world.size.width():
                    posx -= world.size.width()

                moves.append(QPoint(posx, posy))
        return moves

    @abstractmethod
    def make_move(self, oldpos, world):
        """
        Try to move the world object.
        """

    @abstractmethod
    def reproduce(self):
        """
        Try to reproduce the world object. Returns 'None' if there was no baby created.
        """
        return None

    def has_starved(self):
        """
        Informs caller whether world object has starved to death or not.
        """
        return False

    def update(self, currpos, tick, world):
        """
        Update the state of the world object for a given world tick.
        """
        if tick > self._last_update:
            self._last_update = tick
            self._age += 1

            if self.has_starved():
                del world.mobs[currpos]

            elif self.make_move(currpos, world):
                baby = self.reproduce()
                if baby:
                    world.mobs[currpos] = baby


class MobFish(MobBase):
    """
    Implementation of a fish world object.
    """

    def __init__(self, breed, lastupdate=-1):
        super(MobFish, self).__init__(
            "fish", QPixmap("res/sprite_fish.png"), breed, lastupdate)

    def make_move(self, oldpos, world):
        """
        Move a fish world object.
        """
        moved = False

        moves = [move for move in MobBase.generate_move_list(
            oldpos, world) if move not in world.mobs]

        if moves:
            world.mobs[random.choice(moves)] = world.mobs[oldpos]
            del world.mobs[oldpos]
            moved = True

        return moved

    def reproduce(self):
        """
        Check whether a fish should reproduce or not.
        """
        if self._age % self._breed == 0:
            return MobFish(self._breed, self._last_update)
        return None


class MobShark(MobBase):
    """
    Implementation of a shark world object.
    """

    def __init__(self, breed, starve, lastupdate=-1):
        super(MobShark, self).__init__(
            "shark", QPixmap("res/sprite_shark.png"), breed, lastupdate)
        self._starve = starve
        self._full = starve

    def has_starved(self):
        """
        Check whether a shark world object has starved or not.
        """
        self._full -= 1
        return bool(self._full == 0)

    def make_move(self, oldpos, world):
        """
        Move a shark world object.
        """
        moved = False

        moves = MobBase.generate_move_list(oldpos, world)
        fishmoves = [
            move for move in moves if move in world.mobs and
            isinstance(world.mobs[move], MobFish)]
        emptymoves = [move for move in moves if move not in world.mobs]

        if fishmoves:
            world.mobs[random.choice(fishmoves)] = world.mobs[oldpos]
            del world.mobs[oldpos]
            self._full = self._starve
            moved = True
        elif emptymoves:
            world.mobs[random.choice(emptymoves)] = world.mobs[oldpos]
            del world.mobs[oldpos]
            moved = True

        return moved

    def reproduce(self):
        """
        Check whether a shark should reproduce or not.
        """
        if self._age % self._breed == 0:
            return MobShark(self._breed, self._starve, self._last_update)
        return None


class MobWater(MobBase):
    """
    Implementation of a water world object.
    """

    def __init__(self):
        super(MobWater, self).__init__(
            "water", QPixmap("res/sprite_water.png"))

    def make_move(self, oldpos, world):
        """
        Try to move the world object.
        """

    def reproduce(self):
        """
        Try to reproduce the world object. Returns 'None' if there was no baby created.
        """
        return None
