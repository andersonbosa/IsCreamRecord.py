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

    # Gets Width of primary monitor
    def Width(self):
        return self.primary_monitor.width

    # Gets Height of primary monitor
    def Height(self):
        return self.primary_monitor.height

    # Gets resolution of primary monitor
    def Resolution(self):
        return self.width, self.height

    # Error handling
    def seemsLegit(self):
        if self.x_start != 0:
            if self.Width() - (self.x_start + self.get_width()) < 0:
                print("Screenshot out of bounds!")
                exit()

        if self.y_start != 0:
            if self.Height() - (self.y_start + self.get_height()) < 0:
                print("Screenshot out of bounds!")
                exit()

        if self.snapKey.lower() == self.quitKey.lower():
            print("Capture Key and Quit key cannot be the same")
            exit()

    """ Getters """

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_collection(self):
        return self.collection

    def get_items(self):
        items = []
        with os.scandir(self.get_collection()) as dir:
            for entries in dir:
                items.append(entries.name)
        return items

    def get_snap_key(self):
        return self.snapKey

    def get_quit_key(self):
        return self.quitKey

    def get_interval(self):
        return self.interval

    def get_camera(self):
        return self.camera

    def get_x_start(self):
        return self.x_start

    def get_y_start(self):
        return self.y_start

    def get_delay(self):
        return self.delay

    """ setters """

    def set_collection(self, name):
        collectionLoc = os.path.join(os.getcwd(), "collected-data", name)
        if os.path.exists(collectionLoc):
            self.collection = collectionLoc
        else:
            os.mkdir(collectionLoc)
            self.collection = collectionLoc
            print("Subfolder for collection", name, "created in collected-data")

    def set_width(self, width):
        self.width = width

    def set_height(self, height):
        self.height = height

    def set_snap_key(self, snapKey):
        self.snapKey = str(snapKey).lower()

    def set_quit_key(self, quitKey):
        self.quitKey = str(quitKey).lower()

    def set_interval(self, interval):
        self.interval = interval

    def set_camera(self, camera):
        self.camera = int(camera - 1)

    def set_x_start(self, x_start):
        self.x_start = x_start

    def set_y_start(self, y_start):
        self.y_start = y_start

    def set_delay(self, delay):
        self.delay = delay

    """ Functions """

    def _get_collection_path(self):
        return (
            self.get_collection().split(self.directory_divider)[-1]
            + str(len(self.get_items()))
            + ".png"
        )

    # Coordinates start at the top left of the screen.
    # The higher the ystart value, the lower the capture.
    # The higher the xstart value, the farther right it begins.

    def screenshot(self):
        with mss.mss() as screenshooter:
            last_time = time.time()

            # The area of screen to be captured
            monitor = {
                "top": self.y_start,
                # "left": self.x_start,
                "left": self.primary_monitor.x,  # TOFIX: Using two monitors we need to use position x to capture primary monitor correctly.
                "width": self.width,
                "height": self.height,
            }

            # filename gets name of working directory, and creates name of files based on collection.
            filename = self._get_collection_path()

            fileOut = os.path.join(self.get_collection(), filename)

            # Grab the data
            sct_img = screenshooter.grab(monitor)

            # Save to the picture file
            mss.tools.to_png(sct_img.rgb, sct_img.size, output=fileOut)
            self.logger.info(f"fps: {1 / (time.time() - last_time)}")

    # takes screenshots on keypress.
    # snapkey is the key that triggers screenshot
    def sctManual(self, benchmark=25):
        print(f"{self.snapKey} - press to screenshot | {self.quitKey} - press to quit")

        # 2 counts to adjust for the Borat
        count = 0
        imgCount = 0

        while True:
            # if key is pressed take screenshot.
            if self.keyboard.isSnapKeyPressed:
                self.screenshot()
                count += 1
                time.sleep(0.01)

                # every 25 images let us know
                if count % benchmark == 0:
                    count += 1
                    imgCount = count - 1
                    self.logger.info(f"Images Taken: + {str(imgCount)}")

            if self.keyboard.isQuitKeyPressed:
                self.logger.info("Exiting")
                break

    # takes screenshots on time interval.
    def sctAuto(self):
        print(
            f"{self.interval} - interval to screenshot | {self.quitKey} - press to quit"
        )

        if self.delay != 0:
            self.logger.info(f"delay set for: {self.delay}")
            time.sleep(self.delay)
            self.logger.info("starting capture")

        imgCount = 0
        t = int(time.time())

        while True:
            whileTime = int(time.time())

            # every interval take a screenshot
            if whileTime - t > 0 and (whileTime - t) % self.interval == 0:
                self.screenshot()
                imgCount += 1
                time.sleep(1)
                self.logger.info(f"image Count: str(imgCount)")

            if self.keyboard.isQuitKeyPressed:
                self.logger.info(f"{self.quitKey} pressed, Exiting")
                break

        print(f"{imgCount}, Images gathered.")

    # NOTE
    def camManual(self):
        print(f"{self.snapKey} - press to screenshot | {self.quitKey} - press to quit")

        # Camera to be captured
        vid = cv2.VideoCapture(self.camera)
        count = 0
        while True:
            # filename gets name of working directory, and creates name of files based on collection.
            filename = self._get_collection_path()
            fileOut = os.path.join(self.get_collection(), filename)

            ret, frame = vid.read()
            cv2.imshow("IsCreamRecorder", frame)

            # if key is pressed take screenshot.
            if self.keyboard.isSnapKeyPressed:
                self.logger.info("keyboard.isSnapKeyPressed")
                cv2.imwrite(fileOut, frame)
                count += 1
                time.sleep(0.15)

            cv2.waitKey(1)

            # We implement keyboard rather than waitkey & 0xFF To remove lag as well as enable global macro
            if self.keyboard.isQuitKeyPressed:
                self.logger.info("keyboard.isQuitKeyPressed")
                break

        vid.release()
        cv2.destroyAllWindows()

        print(f"{str(count)}, Images gathered.")

    def camAuto(self):
        print(
            f"{self.interval} - interval to screenshot | {self.quitKey} - press to quit"
        )

        if self.delay != 0:
            self.logger.info(f"delay set for: {self.delay}")
            time.sleep(self.delay)
            self.logger.info("starting capture")

        # Camera to be captured
        vid = cv2.VideoCapture(self.camera)
        count = 0
        t = int(time.time())
        while True:
            whileTime = int(time.time())

            # filename gets name of working directory, and creates name of files based on collection.
            filename = self._get_collection_path()
            fileOut = os.path.join(self.get_collection(), filename)

            ret, frame = vid.read()
            cv2.imshow("IsCreamRecorder", frame)

            # every interval take a screenshot
            if (whileTime - t) > 0 and (whileTime - t) % self.interval == 0:
                cv2.imwrite(fileOut, frame)
                count += 1
                time.sleep(1)
                print(f"image Count: {str(count)}")

            cv2.waitKey(1)

            # We implement keyboard rather than waitkey & 0xFF To remove lag as well as enable global macro
            if self.keyboard.isQuitKeyPressed:
                self.logger.info("keyboard.isQuitKeyPressed")
                break

        vid.release()
        cv2.destroyAllWindows()

        print(f"{str(count)}, Images gathered.")


if __name__ == "__main__":
    s = IsCreamRecorder()
    s.screenshot()  # DONE
    # s.sctManual() # DONE
    # s.camManual() # DONE
    # s.camAuto()   # DONE
    pass
