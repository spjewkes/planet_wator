# -*- coding: utf-8 -*-
"""
Stores the settings needed by the Planet Wa-Tor application.
"""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QSlider, QPushButton, QLabel
from PySide6.QtCore import Qt


class Settings(QDialog):
    """
    Class for managing the settings of the application. This class is
    also a QT dialog box and can be used to interactively alter the
    settings.
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
