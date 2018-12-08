import threading
from VendApi import *
import re
from VendGetGUI import *
import CsvUtil
import datetime as dt

api = None

def start(gui):

    if not gui.entriesHaveValues():
        ## error
        gui.setStatus("Please have values for prefix, token and dates...")
        gui.setReadyState()
        return

    pattern = re.compile("^\d{4}(-\d{2}){2}")

    if pattern.match(gui.getDateFrom()) is None:
        gui.setStatus("Please make sure date-from is in YYYY-mm-dd format...")
        gui.setReadyState()
        return

    if pattern.match(gui.getDateTo()) is None:
        gui.setStatus("Please make sure date-to is in YYYY-mm-dd format...")
        gui.setReadyState()
        return
