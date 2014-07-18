import sys
import socket
import logging
import xmlrpclib

import asi
from asi.manager import RunManager

asi.log.init_logging("runman.log")

logger = logging.getLogger(__name__)

logger.info("Starting!")

try:
    scheduler = asi.client.Scheduler()
    logger.info("Connected to scheduler: " + scheduler.name())

except socket.error:
    logger.critical("Could not connect to scheduler")
    sys.exit()

logger.info("Resetting scheduler...")
scheduler.reset()

try:
    telescope = asi.client.Telescope()
    logger.info("Connected to telescope: " + telescope.name())

except socket.error:
    logger.critical("Could not connect to telescope")
    sys.exit()

try:
    slider = asi.client.Slider()
    logger.info("Connected to slider: " + slider.name())

except socket.error:
    logger.critical("Could not connect to slider")
    sys.exit()

#focuser = asi.focuser.focusmax.FocusMaxFocuser()
focuser = asi.focuser.simulator.SimulatorFocuser()

try:
    science_camera = asi.client.ScienceCamera()
    logger.info("Connected to science camera: " + science_camera.name())
except socket.error:
    logger.critical("Could not connect to science camera")
    sys.exit()

rm = RunManager(scheduler, telescope, slider, focuser, science_camera)

while 1:
    rm.update()

logger.info("Goodbye!")
