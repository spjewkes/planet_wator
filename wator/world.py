# -*- coding: utf-8 -*-
"""
Defines the world of planet Wa-Tor.
"""

import random

from PySide2.QtWidgets import QWidget
from PySide2.QtGui import QPainter
from PySide2.QtCore import QPoint

from wator.mobs import MobWater, MobShark, MobFish


class World:
    """
    Class for managing an instance of the world Wa-Tor.
    """

    def __init__(self, size, settings):
        self._size = size
        self._chronons = 0
        self._mobs = None

        self.reset(settings)

    @property
    def size(self):
        """
        The size of the planet in tiles.
        """
        return self._size

    @property
    def mobs(self):
        """
        Returns a dictionary of the objects inhabiting the world. The key is the world
        coordinate of the object.
        """
        return self._mobs

    def reset(self, settings):
        """
        Reset the world.
        """
        points = list()
        for y in range(self._size.height()):
            for x in range(self._size.width()):
                points.append(QPoint(x, y))
        random.shuffle(points)

        self._mobs = dict()
        for _ in range(settings.nsharks):
            self.mobs[points.pop(0)] = MobShark(
                settings.sbreed, settings.starve)

        for _ in range(settings.nfish):
            self.mobs[points.pop(0)] = MobFish(settings.fbreed)

    def update(self, tick):
        """
        Update the world state.
        """
        copy = {k: v for k, v in self.mobs.items() if v}
        for pos, mob in copy.items():
            mob.update(pos, tick, self)

    def stats(self):
        """
        Return the number of fish and sharks that are currently inhabiting the world.
        """
        fish = len([mob for mob in self.mobs.values()
                    if isinstance(mob, MobFish)])
        sharks = len([mob for mob in self.mobs.values()
                      if isinstance(mob, MobShark)])
        return fish, sharks


class WaTorWidget(QWidget):
    """
    Defines widget for displaying and handling the display of planet Wa-Tor.
    """

    def __init__(self, world, parent=None):
        super(WaTorWidget, self).__init__(parent)
        self._size = world.size
        self._scale = 16
        self._widget_size = self._size * self._scale
        self._world = world
        self._water = MobWater()

    def sizeHint(self):
        """
        The size of the WaTor widget in pixels.
        """
        return self._widget_size

    def minimumSizeHint(self):
        """
        The minimum size of the WaTor widget in pixels.
        """
        return self._widget_size

    def paintEvent(self, event):
        """
        Paint the widget.
        """
        super(WaTorWidget, self).paintEvent(event)

        painter = QPainter(self)

        for y in range(self._size.height()):
            for x in range(self._size.width()):
                pos = QPoint(x, y) * self._scale
                painter.drawPixmap(pos, self._water.pixmap)

        for pos, mob in self._world.mobs.items():
            painter.drawPixmap(pos * self._scale, mob.pixmap)

        painter.end()
