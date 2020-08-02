#!/usr/bin/env python3

import sys
import random

from PySide2 import QtCore, Qt
from PySide2.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QAction, QMenuBar, QMainWindow
from PySide2.QtGui import QPainter, QColor, QPixmap, QIcon
from PySide2.QtCore import QSize, QPoint, Slot, QTimer


class WorldBase:
    def __init__(self, name, pixmap, breed=0, lastupdate=-1):
        self._name = name
        self._pixmap = pixmap
        self._breed = breed
        self._age = 0
        self._lastUpdate = lastupdate

    @property
    def name(self):
        return self._name

    @property
    def pixmap(self):
        return self._pixmap

    @staticmethod
    def generateMoveList(pos, world):
        moves = list()
        for y in (-1, 0, 1):
            posy = pos.y() + y
            if posy < 0:
                posy += world.size.height()
            elif posy >= world.size.height():
                posy -= world.size.height()
            for x in (-1, 0,  1):
                if y == 0 and x == 0:
                    continue
                posx = pos.x() + x
                if posx < 0:
                    posx += world.size.width()
                elif posx >= world.size.width():
                    posx -= world.size.width()

                moves.append(QPoint(posx, posy))
        return moves

    def makeMove(self, oldpos, world):
        pass

    def reproduce(self):
        pass

    def hasStarved(self):
        return False

    def update(self, currpos, tick, world):
        if tick > self._lastUpdate:
            self._lastUpdate = tick
            self._age += 1

            if self.hasStarved():
                del world.mobs[currpos]

            elif self.makeMove(currpos, world):
                baby = self.reproduce()
                if baby:
                    world.mobs[currpos] = baby


class WorldFish(WorldBase):
    def __init__(self, breed, lastupdate=-1):
        super(WorldFish, self).__init__(
            "fish", QPixmap("sprite_fish.png"), breed, lastupdate)

    def makeMove(self, oldpos, world):
        moved = False

        moves = [move for move in WorldBase.generateMoveList(
            oldpos, world) if move not in world.mobs]

        if moves:
            world.mobs[random.choice(moves)] = world.mobs[oldpos]
            del world.mobs[oldpos]
            moved = True

        return moved

    def reproduce(self):
        if self._age % self._breed == 0:
            return WorldFish(self._breed, self._lastUpdate)
        return None


class WorldShark(WorldBase):
    def __init__(self, breed, starve, lastupdate=-1):
        super(WorldShark, self).__init__(
            "shark", QPixmap("sprite_shark.png"), breed, lastupdate)
        self._starve = starve
        self._full = starve

    def hasStarved(self):
        self._full -= 1
        return bool(self._full == 0)

    def makeMove(self, oldpos, world):
        moved = False

        moves = WorldBase.generateMoveList(oldpos, world)
        fishmoves = [
            move for move in moves if move in world.mobs and type(world.mobs[move]) == WorldFish]
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
        if self._age % self._breed == 0:
            return WorldShark(self._breed, self._starve, self._lastUpdate)
        return None


class WorldWater(WorldBase):
    def __init__(self):
        super(WorldWater, self).__init__(
            "water", QPixmap("sprite_water.png"))


class World:
    def __init__(self, size, scale):
        self._size = size
        self._scale = scale
        self._nsharks = 20
        self._nfish = 200
        self._fbreed = 3
        self._sbreed = 10
        self._starve = 3
        self._chronons = 0
        self._mobs = None
        self._water = WorldWater()

        self.reset()

    @property
    def size(self):
        return self._size

    @property
    def mobs(self):
        return self._mobs

    def reset(self):
        points = list()
        for y in range(self._size.height()):
            for x in range(self._size.width()):
                points.append(QPoint(x, y))
        random.shuffle(points)

        self._mobs = dict()
        for _ in range(self._nsharks):
            self.mobs[points.pop(0)] = WorldShark(self._sbreed, self._starve)

        for _ in range(self._nfish):
            self.mobs[points.pop(0)] = WorldFish(self._fbreed)

    def draw(self, painter):
        for y in range(self._size.height()):
            for x in range(self._size.width()):
                pos = QPoint(x, y) * self._scale
                painter.drawPixmap(pos, self._water.pixmap)

        for pos, mob in self.mobs.items():
            painter.drawPixmap(pos * self._scale, mob.pixmap)

    def update(self, tick):
        copy = {k: v for k, v in self.mobs.items() if v}
        for pos, mob in copy.items():
            mob.update(pos, tick, self)

    def stats(self):
        fish = len([mob for mob in self.mobs.values()
                    if type(mob) == WorldFish])
        shark = len([mob for mob in self.mobs.values()
                     if type(mob) == WorldShark])
        return fish, shark


class WaTorWidget(QWidget):
    """
    Defines widget for displaying and handling the display of planet Wa-Tor.
    """

    def __init__(self, parent=None):
        super(WaTorWidget, self).__init__(parent)
        self._size = QSize(80, 23)
        self._scale = 16
        self._ticks = 0
        self._widgetSize = self._size * self._scale
        self._updater = QTimer(self)
        self._updater.timeout.connect(self._update)

        self._world = World(self._size, self._scale)

    def sizeHint(self):
        return self._widgetSize

    def minimumSizeHint(self):
        return self._widgetSize

    def paintEvent(self, event):
        super(WaTorWidget, self).paintEvent(event)

        painter = QPainter(self)
        self._world.draw(painter)
        painter.end()

    def play(self):
        self._updater.start(250)

    def pause(self):
        self._updater.stop()

    def _update(self):
        self._world.update(self._ticks)
        self._ticks += 1
        self.repaint()
        print(self._world.stats())


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setWindowTitle("Planet Wa-Tor")
        self.setWindowIcon(QIcon("icon_wator.png"))
        self.setCentralWidget(QWidget())

        self._watorWidget = WaTorWidget()
        self.home()

    def home(self):
        buttons = QHBoxLayout()
        # Play button
        play_button = QPushButton("Play")
        play_button.clicked.connect(self._play)
        buttons.addWidget(play_button)
        # Pause button
        pause_button = QPushButton("Pause")
        pause_button.clicked.connect(self._pause)
        buttons.addWidget(pause_button)
        # Quit button
        quit_button = QPushButton("Quit")
        quit_button.clicked.connect(self._quit)
        buttons.addWidget(quit_button)

        layout = QVBoxLayout()
        layout.addWidget(self._watorWidget)
        layout.addSpacing(10)
        layout.addLayout(buttons)

        self.centralWidget().setLayout(layout)

    @Slot()
    def _quit(self):
        QtCore.QCoreApplication.instance().quit()

    @Slot()
    def _play(self):
        self._watorWidget.play()

    @Slot()
    def _pause(self):
        self._watorWidget.pause()


if __name__ == "__main__":
    # Create the Qt Application
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon_wator.png"))
    # Create and show the form
    mainWindow = MainWindow()
    mainWindow.show()
    # Run the main Qt loop
    sys.exit(app.exec_())
