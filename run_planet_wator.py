#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Application that runs an implementation of Planet Wa-Tor using Python and QT.
"""

import sys

from PySide2 import QtCore
from PySide2.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QWidget, QMainWindow, \
    QAction, QSlider, QDialog, QLabel
from PySide2.QtGui import QPainter, QIcon
from PySide2.QtCore import QSize, Slot, QTimer, Qt

from wator.settings import Settings
from wator.world import World


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
