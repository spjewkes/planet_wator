# -*- coding: utf-8 -*-
"""
Defines the world of planet Wa-Tor.
"""

import random

from PySide2.QtWidgets import QWidget
from PySide2.QtGui import QPainter
from PySide2.QtCore import QPoint, QSize
from PIL import Image, ImageDraw
from PIL.ImageQt import ImageQt

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


class WaTorGraph(QWidget):
    """
    Defines widget for displaying graph of stats of planet Wa-Tor
    """

    def __init__(self, world, parent=None):
        super(WaTorGraph, self).__init__(parent)
        size = QSize(world.size.width(), 10)
        scale = 16
        self._widget_size = size * scale
        self._world = world
        self._tick = 0
        self._prev_shark = 0
        self._prev_fish = 0
        self._prev_tick = 0

        self._scaler = world.size.width() * world.size.height() + 1

        self._image = Image.new(
            "RGB", self._widget_size.toTuple(), (255, 255, 255))
        self.reset()

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

    def helper_calc_y_pos(self, y):
        """
        Calculates absolute y position in the widget using pre-calculated scaler.
        """
        return self._widget_size.height() - int((y / self._scaler) * self._widget_size.height()) - 1

    def reset(self):
        """
        Reset the graph.
        """
        self._tick = 0
        self._prev_shark = self.helper_calc_y_pos(0)
        self._prev_fish = self.helper_calc_y_pos(0)
        self._prev_tick = 0

        draw = ImageDraw.Draw(self._image)
        draw.rectangle([(0, 0), self._image.size], (127, 127, 127))

    def paintEvent(self, event):
        """
        Paint the widget.
        """
        super(WaTorGraph, self).paintEvent(event)

        painter = QPainter(self)

        fish, sharks = self._world.stats()

        shark = self.helper_calc_y_pos(sharks)
        fish = self.helper_calc_y_pos(fish)

        draw = ImageDraw.Draw(self._image)
        draw.line([(self._prev_tick, self._prev_shark),
                   (self._tick, shark)], (0, 0, 255), 2)
        draw.line([(self._prev_tick, self._prev_fish),
                   (self._tick, fish)], (0, 255, 0), 2)

        painter.drawImage(QPoint(0, 0), ImageQt(self._image))
        painter.end()

        self._prev_tick = self._tick
        self._prev_shark = shark
        self._prev_fish = fish
        self._tick += 2

        if self._tick >= self._widget_size.width():
            self.reset()
