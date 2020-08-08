#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Application that runs an implementation of Planet Wa-Tor using Python and QT.
"""

import sys

from PySide2 import QtCore
from PySide2.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QWidget, QMainWindow, \
    QAction, QSlider, QDialog, QLabel
from PySide2.QtGui import QIcon
from PySide2.QtCore import Qt, QTimer, QSize

from wator.settings import Settings
from wator.world import World, WaTorWidget


class MainWindow(QMainWindow):
    """
    Main application entry-point for Wa-Tor.
    """

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self._playing = False
        self._tickpause = 50
        self._size = QSize(80, 40)
        self._settings = Settings()
        self._world = World(self._size, self._settings)

        self._ticks = 0
        self._updater = QTimer(self)
        self._updater.timeout.connect(self._tick)

        self.setWindowTitle("Planet Wa-Tor")
        self.setWindowIcon(QIcon("res/icon_wator.png"))
        self.setCentralWidget(QWidget())

        self._wator_widget = WaTorWidget(self._world)
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
        slider.setValue(self._tickpause)
        slider_layout.addWidget(slider)
        layout.addLayout(slider_layout)

        self.centralWidget().setLayout(layout)

    def _quit(self):
        """
        Quit the application.
        """
        QtCore.QCoreApplication.instance().quit()

    def play(self):
        """
        Start running (or resume) the simulation.
        """
        self._updater.start(self._tickpause * 5)
        self._playing = True

    def pause(self):
        """
        Pause the running of the simulation.
        """
        self._playing = False
        self._updater.stop()

    def reset(self):
        """
        Reset the application.
        """
        self._ticks = 0
        self.pause()
        if self._settings.exec_() == QDialog.Accepted:
            self._world.reset(self._settings)
            self._wator_widget.repaint()

    def toolbar_pressed(self, action):
        """
        Handle a button being pressed on the toolbar.
        """
        actions = {"Play": self.play, "Pause": self.pause,
                   "Quit": self._quit, "Reset": self.reset}
        actions[action.text()]()

    def _set_tick_value(self, value):
        self._tickpause = value
        if self._playing:
            self.pause()
            self.play()

    def _tick(self):
        """
        Tick the world simulation.
        """
        self._ticks += 1
        self._world.update(self._ticks)
        self._wator_widget.repaint()

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


if __name__ == "__main__":
    # Create the Qt Application
    APP = QApplication(sys.argv)
    APP.setWindowIcon(QIcon("res/icon_wator.png"))
    # Create and show the form
    MAIN = MainWindow()
    MAIN.show()
    # Run the main Qt loop
    sys.exit(APP.exec_())
