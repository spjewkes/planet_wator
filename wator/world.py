# -*- coding: utf-8 -*-
"""
Defines the world of planet Wa-Tor.
"""

import random

from PySide2.QtWidgets import QWidget
from PySide2.QtGui import QPainter
from PySide2.QtCore import QPoint, QSize, QTimer

from wator.mobs import MobWater, MobShark, MobFish


class World:
    """
    Class for managing an instance of the world Wa-Tor.
    """

    def __init__(self, size, scale, settings):
        self._size = size
        self._scale = scale
        self._chronons = 0
        self._mobs = None
        self._water = MobWater()

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

    def draw(self, painter):
        """
        Draw the state of the world to the window.
        """
        for y in range(self._size.height()):
            for x in range(self._size.width()):
                pos = QPoint(x, y) * self._scale
                painter.drawPixmap(pos, self._water.pixmap)

        for pos, mob in self.mobs.items():
            painter.drawPixmap(pos * self._scale, mob.pixmap)

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

    def __init__(self, settings, parent=None):
        super(WaTorWidget, self).__init__(parent)
        self._size = QSize(80, 23)
        self._scale = 16
        self._ticks = 0
        self._widget_size = self._size * self._scale
        self._updater = QTimer(self)
        self._updater.timeout.connect(self._update)

        self._world = World(self._size, self._scale, settings)

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
        self._world.draw(painter)
        painter.end()

    def reset(self, settings):
        """
        Reset the simulation.
        """
        self.pause()
        self._world.reset(settings)
        self.repaint()

    def play(self, rate):
        """
        Start or resume running the simulation.
        """
        self._updater.start(rate)

    def pause(self):
        """
        Pause the running of the simulation.
        """
        self._updater.stop()

    def _update(self):
        """
        Update the simulation by one tick.
        """
        self._world.update(self._ticks)
        self._ticks += 1
        self.repaint()
        fish, sharks = self._world.stats()
        if fish == 0 and sharks == 0:
            print("Both sharks and fish have become extinct.")
            self.pause()
        elif fish == 0 and sharks > 0:
            print("No more fish. Wa-Tor is overrun with sharks.")
            self.pause()
        elif sharks == 0:
            print("No more sharks. Wa-Tor will become overrun with fish.")
            self.pause()
        print("Fish: {} - Sharks: {}".format(fish, sharks))
