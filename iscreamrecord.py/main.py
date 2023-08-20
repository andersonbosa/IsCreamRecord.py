import os
import mss
from mss import mss
import mss.tools
import ctypes
import numpy
import cv2
import time
import random
import sys
import logging
from pynput import keyboard
from screeninfo import get_monitors


class Utils:
    def is_windows_system():
        return os.name == "nt"

    def get_primary_monitor():
        l = list(filter(lambda monitor: monitor.is_primary, get_monitors()))

        if len(l) <= 0:
            raise Error("Primary monitor not found")

        return l[0]


# REFACTOR: id:LeB9n0Yta
class KeyboardListener:
    def __init__(self, snapKey, quitKey):
        self.snapKey = snapKey
        self.isSnapKeyPressed = False

        self.quitKey = quitKey
        self.isQuitKeyPressed = False

        self.listener = keyboard.Listener(on_press=self.on_key_press)
        self.listener.start()

    def on_key_press(self, key):
        try:
            if key.char == self.snapKey:
                self.isSnapKeyPressed = True
                time.sleep(0.03)  # NOTE: Less than 0.03 struggles to work
                self.isSnapKeyPressed = False

            elif key.char == self.quitKey:
                self.isQuitKeyPressed = True

        except AttributeError:
            pass  # Ignore non-character keys


class IsCreamRecorder:
    # Attributes
    res = 0
    width = 0
    height = 0
    collection = None
    items = None
    snapKey = ""
    quitKey = ""
    interval = 5
    delay = 0
    camera = 0

    # Initializes Class
    def __init__(self):
        self.logger = self._setup_logger()

        self.x_start = 0
        self.y_start = 0
        self.delay = 1
        self.camera = 0
        self.interval = 1
        self.directory_divider = "/"

        # REFACTOR: id:LeB9n0Yta: acoplado com keyboard listener o funcionamento. melhorar tornando desacoplado
        self.snapKey = "p".lower()
        self.quitKey = "q".lower()
        self.keyboard = KeyboardListener(
            snapKey=self.snapKey,
            quitKey=self.quitKey,
        )

        self.primary_monitor = Utils.get_primary_monitor()
        self.width = self.Width()
        self.height = self.Height()
        self.res = self.Resolution()

        self.items = self.get_items()
        self.collection = os.path.join(os.getcwd(), "collected-data")

    #
    # Setups methods
    #
    def _setup_logger(self):
        logger = logging.getLogger("IsCreamRecorder")
        logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            "[%(asctime)s][%(levelname)s][%(process)s][%(pathname)s:%(lineno)s]: %(message)s",
        )

        # File handler for logging to a file
        file_handler = logging.FileHandler("iscreamrecord.py.log")
        file_handler.setFormatter(formatter)

        # Stream handler for logging to console
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

        return logger
