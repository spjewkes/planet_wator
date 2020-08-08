#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Application that runs an implementation of Planet Wa-Tor using Python and QT.
"""

import sys
import random
from abc import ABC, abstractmethod

from PySide2 import QtCore
from PySide2.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QWidget, QMainWindow, \
    QAction, QSlider, QDialog, QPushButton, QLabel
from PySide2.QtGui import QPainter, QPixmap, QIcon
from PySide2.QtCore import QSize, QPoint, Slot, QTimer, Qt


class WorldBase(ABC):
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


class WorldFish(WorldBase):
    """
    Implementation of a fish world object.
    """

    def __init__(self, breed, lastupdate=-1):
        super(WorldFish, self).__init__(
            "fish", QPixmap("res/sprite_fish.png"), breed, lastupdate)

    def make_move(self, oldpos, world):
        """
        Move a fish world object.
        """
        moved = False

        moves = [move for move in WorldBase.generate_move_list(
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
            return WorldFish(self._breed, self._last_update)
        return None


class WorldShark(WorldBase):
    """
    Implementation of a shark world object.
    """

    def __init__(self, breed, starve, lastupdate=-1):
        super(WorldShark, self).__init__(
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

        moves = WorldBase.generate_move_list(oldpos, world)
        fishmoves = [
            move for move in moves if move in world.mobs and
            isinstance(world.mobs[move], WorldFish)]
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
            return WorldShark(self._breed, self._starve, self._last_update)
        return None


class WorldWater(WorldBase):
    """
    Implementation of a water world object.
    """

    def __init__(self):
        super(WorldWater, self).__init__(
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


class World:
    """
    Class for managing an instance of the world Wa-Tor.
    """

    def __init__(self, size, scale, settings):
        self._size = size
        self._scale = scale
        self._chronons = 0
        self._mobs = None
        self._water = WorldWater()

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
            self.mobs[points.pop(0)] = WorldShark(
                settings.sbreed, settings.starve)

        for _ in range(settings.nfish):
            self.mobs[points.pop(0)] = WorldFish(settings.fbreed)

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
                    if isinstance(mob, WorldFish)])
        sharks = len([mob for mob in self.mobs.values()
                      if isinstance(mob, WorldShark)])
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


class Settings(QDialog):
    """
    Dialog box for changing settings.
    """

    def __init__(self):
        super(Settings, self).__init__()

        self._nsharks = 20
        self._nfish = 200
        self._fbreed = 3
        self._sbreed = 10
        self._starve = 3

        self.home()

    @staticmethod
    def helper_create_slider(interval, minrange, maxrange, value):
        """
        Utility function to create a slider bar for the settings dialog.
        """
        slider = QSlider()
        slider.setTickPosition(QSlider.TicksBothSides)
        slider.setTickInterval(interval)
        slider.setRange(minrange, maxrange)
        slider.setSingleStep(1)
        slider.setOrientation(Qt.Horizontal)
        slider.setValue(value)
        slider.setFixedWidth(500)
        return slider

    def home(self):
        """
        Set up the layout of the setting dialog.
        """
        layout = QVBoxLayout()

        nfish_layout = QHBoxLayout()
        nfish_layout.addWidget(QLabel("Number of Fish", self))
        self.nfish_slider = Settings.helper_create_slider(
            25, 0, 500, self._nfish)
        nfish_layout.addWidget(self.nfish_slider)
        layout.addLayout(nfish_layout)

        fbreed_layout = QHBoxLayout()
        fbreed_layout.addWidget(QLabel("Fish Breed Ticks", self))
        self.fbreed_slider = Settings.helper_create_slider(
            1, 1, 15, self._fbreed)
        fbreed_layout.addWidget(self.fbreed_slider)
        layout.addLayout(fbreed_layout)

        nsharks_layout = QHBoxLayout()
        nsharks_layout.addWidget(QLabel("Number of Sharks", self))
        self.nsharks_slider = Settings.helper_create_slider(
            25, 0, 500, self._nsharks)
        nsharks_layout.addWidget(self.nsharks_slider)
        layout.addLayout(nsharks_layout)

        sbreed_layout = QHBoxLayout()
        sbreed_layout.addWidget(QLabel("Shark Breed Ticks", self))
        self.sbreed_slider = Settings.helper_create_slider(
            1, 1, 15, self._sbreed)
        sbreed_layout.addWidget(self.sbreed_slider)
        layout.addLayout(sbreed_layout)

        starve_layout = QHBoxLayout()
        starve_layout.addWidget(QLabel("Shark Starve Ticks", self))
        self.starve_slider = Settings.helper_create_slider(
            1, 1, 30, self._starve)
        starve_layout.addWidget(self.starve_slider)
        layout.addLayout(starve_layout)

        cancel_ok_layout = QHBoxLayout()
        cancel_button = QPushButton("&Cancel", self)
        cancel_button.clicked.connect(self._cancel)
        cancel_ok_layout.addWidget(cancel_button)
        ok_button = QPushButton("&Reset", self)
        ok_button.clicked.connect(self._okay)
        cancel_ok_layout.addWidget(ok_button)

        layout.addLayout(cancel_ok_layout)

        self.setLayout(layout)

    def _cancel(self):
        self.reject()

    def _okay(self):
        self._nsharks = self.nsharks_slider.value()
        self._nfish = self.nfish_slider.value()
        self._fbreed = self.fbreed_slider.value()
        self._sbreed = self.sbreed_slider.value()
        self._starve = self.starve_slider.value()

        self.accept()

    @property
    def nsharks(self):
        """
        Number of sharks at start,
        """
        return self._nsharks

    @property
    def nfish(self):
        """
        Number of fish at start.
        """
        return self._nfish

    @property
    def fbreed(self):
        """
        Number of ticks it takes for a fish to breed.
        """
        return self._fbreed

    @property
    def sbreed(self):
        """
        Number of ticks it takes for a shark to breed.
        """
        return self._sbreed

    @property
    def starve(self):
        """
        Number of ticks before a sharks dies (if it hasn't eaten).
        """
        return self._starve


class MainWindow(QMainWindow):
    """
    Main application entry-point for Wa-Tor.
    """

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self._playing = False
        self._ticks = 50
        self._settings = Settings()

        self.setWindowTitle("Planet Wa-Tor")
        self.setWindowIcon(QIcon("res/icon_wator.png"))
        self.setCentralWidget(QWidget())

        self._wator_widget = WaTorWidget(self._settings)
        self.home()

    def home(self):
        """
        Add the GUI elements to the window that represent the home state of the application.
        """
        toolbar = self.addToolBar("File")
        play = QAction(QIcon("res/icon_play.png"), "Play", self)
        toolbar.addAction(play)
        pause = QAction(QIcon("res/icon_pause.png"), "Pause", self)
        toolbar.addAction(pause)
        toolbar.addSeparator()
        quit_app = QAction(QIcon("res/icon_quit.png"), "Quit", self)
        toolbar.addAction(quit_app)
        toolbar.addSeparator()
        reset = QAction(QIcon("res/icon_reset.png"), "Reset", self)
        toolbar.addAction(reset)
        toolbar.actionTriggered[QAction].connect(self.toolbar_pressed)

        layout = QVBoxLayout()
        layout.addWidget(self._wator_widget)

        slider_layout = QHBoxLayout()
        slider_layout.addWidget(QLabel("Tick Speed", self))
        slider = QSlider()
        slider.setTickPosition(QSlider.TicksBothSides)
        slider.setTickInterval(25)
        slider.setRange(0, 500)
        slider.setSingleStep(1)
        slider.setOrientation(Qt.Horizontal)
        slider.valueChanged.connect(self._set_tick_value)
        slider.setValue(self._ticks)
        slider_layout.addWidget(slider)
        layout.addLayout(slider_layout)

        self.centralWidget().setLayout(layout)

    @ Slot()
    def _quit(self):
        """
        Quit the application.
        """
        QtCore.QCoreApplication.instance().quit()

    @ Slot()
    def _play(self):
        """
        Start running (or resume) the simulation.
        """
        self._wator_widget.play(self._ticks * 5)
        self._playing = True

    @ Slot()
    def _pause(self):
        """
        Pause the running of the simulation.
        """
        self._wator_widget.pause()
        self._playing = False

    def toolbar_pressed(self, action):
        """
        Handle a button being pressed on the toolbar.
        """
        print(action.text)
        if action.text() == "Play":
            self._play()
        elif action.text() == "Pause":
            self._pause()
        elif action.text() == "Quit":
            QtCore.QCoreApplication.instance().quit()
        elif action.text() == "Reset":
            self._pause()
            if self._settings.exec_() == QDialog.Accepted:
                self._wator_widget.reset(self._settings)

    def _set_tick_value(self, value):
        self._ticks = value
        if self._playing:
            self._pause()
            self._play()


if __name__ == "__main__":
    # Create the Qt Application
    APP = QApplication(sys.argv)
    APP.setWindowIcon(QIcon("res/icon_wator.png"))
    # Create and show the form
    MAIN = MainWindow()
    MAIN.show()
    # Run the main Qt loop
    sys.exit(APP.exec_())
