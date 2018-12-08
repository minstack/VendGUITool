import threading
from VendApi import *
import re
from VendGetGUI import *
import CsvUtil
import datetime as dt

api = None
START_DAY_TIME = "00:00"
END_DAY_TIME = "23:59"

def start(getGui):

    global gui
    gui = getGui
    if not gui.entriesHaveValues():
        ## error
        gui.setStatus("Please have values for prefix, token and dates...")
        gui.setReadyState()
        return

    pattern = re.compile("^\d{4}(-\d{2}){2}")
    localDateFrom = gui.getDateFrom()
    localDateTo = gui.getDateTo()

    if pattern.match(localDateTo) is None:
        gui.setStatus("Please make sure date-from is in YYYY-mm-dd format...")
        gui.setReadyState()
        return

    if pattern.match(localDateFrom) is None:
        gui.setStatus("Please make sure date-to is in YYYY-mm-dd format...")
        gui.setReadyState()
        return



    global api
    api = VendApi(gui.getPrefix(), gui.getToken())
    objType = gui.getSelectedType()
    timezone = getTimeZone(api)

    utcDateFrom = ControlUtil.getUtcTime(localDateFrom, START_DAY_TIME, timezone)
    utcDateTo = ControlUtil.getUtcTime(localDateTo, END_DAY_TIME, timezone)

    vendObjs = getVendObjects(api, utcDateFrom, utcDateTo, objType)


def getVendObjects(api, utcDateFrom, utcDateTo, entityType):
    endpointCall = {
        "customers" : api.getCustomers,
        "products" : api.getProducts
    }

    objects = endpointCall[entityType]()

    print(objects)
    print(len(objects))

def getTimeZone(api):
    global outlets

    outlets = api.getOutlets()

    outlet = getMostUpdatedOutlet(outlets)

    return outlet['time_zone']


def getMostUpdatedOutlet(outlets):

    maxVersion = 0
    maxOutlet = None

    for o in outlets:
        currVer = o['version']
        if  currVer > maxVersion:
            maxVersion = currVer
            maxOutlet = o


    return maxOutlet
