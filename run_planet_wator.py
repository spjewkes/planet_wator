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
from PySide2.QtCore import Slot, Qt

from wator.settings import Settings
from wator.world import WaTorWidget


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
