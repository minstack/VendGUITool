import threading
from VendApi import *
import re
from VendGetGUI import *
import CsvUtil
from datetime import datetime as dt
from os.path import expanduser

api = None
START_DAY_TIME = "00:00"
END_DAY_TIME = "23:59"

def startRetrieve(getGui, callback=None):

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

    gui.setStatus("Converting time to UTC format...")
    utcDateFrom = ControlUtil.getUtcTime(localDateFrom, START_DAY_TIME, timezone)
    utcDateTo = ControlUtil.getUtcTime(localDateTo, END_DAY_TIME, timezone)

    gui.setStatus("Retrieving {0} for {1}...".format(objType, gui.getPrefix()))
    vendObjs = getVendObjects(api, utcDateFrom, utcDateTo, objType)

    if len(vendObjs) == 0:
        gui.setStatus("There was nothing returned. Please check your dates...")
        gui.setReadyState()
        return

    gui.setStatus("Retrieved {0} {1}...".format(len(vendObjs), objType))

    objColHeader = {
        "Products" : "id",
        "Customers" : "customer_code"
    }

    currCsvHeader = objColHeader[objType]

    listToWrite = getColumnList(vendObjs, currCsvHeader)
    gui.setStatus("Exporting temp CSV for bulk delete...")
    filepath = exportToCsv(listToWrite, currCsvHeader, objType)
    filename = filepath.split('/')[-1]

    msg = "Exported {0} {1} to {2}\ntemporarily to desktop.\n\n".format(len(vendObjs), objType, filename)
    msg += "You can now go to Bulk Delete tab to delete."
    gui.setResult(msg)
    gui.setStatus('Done...')
    gui.setReadyState()

    if callback:
        kargs = {
            'prefix' : gui.getPrefix(),
            'token' : gui.getToken(),
            'filepath' : filepath,
            'filename' : filename,
            'entity' : entityType
        }

        callback(kwargs=kargs)

def exportToCsv(list, header, type):
    return CsvUtil.writeListToCSV(list, header, type, "")

def getColumnList(objs, header):
    list = []
    for o in objs:
        list.append(o[header])

    return list


def getVendObjects(api, utcDateFrom, utcDateTo, entityType):
    endpointCall = {
        "Customers" : api.getCustomers,
        "Products" : api.getProducts
    }

    objects = endpointCall[entityType]()

    filteredObj = filterByDateRange(objects, utcDateFrom, utcDateTo)

    return filteredObj

def filterByDateRange(objs, dateFrom, dateTo):

    filtered = []
    dtfmt = "%Y-%m-%d %H:%M"
    dFrom = dt.strptime(dateFrom, dtfmt)
    dTo = dt.strptime(dateTo, dtfmt)

    for o in objs:
        otime = o['created_at'].replace('T', ' ')
        otime = otime[:16]
        oDate = dt.strptime(otime, dtfmt)

        if dFrom <= oDate <= dTo:
            filtered.append(o)

    return filtered

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
