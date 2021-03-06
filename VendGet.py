import threading
from VendApi import *
import re
from VendGetGUI import *
from GitHubApi import *
import CsvUtil
from datetime import datetime as dt
from os.path import expanduser
import getpass
import traceback
from ToolUsageSheets import *

api = None
START_DAY_TIME = "00:00"
END_DAY_TIME = "23:59"

USER = getpass.getuser()
APP_FUNCTION = "VendFilteredRetreive"

def startRetrieve(getGui, callback=None):

    global gui
    gui = getGui
    if not gui.entriesHaveValues():
        ## error
        gui.setStatus("Please have values for prefix, token and dates.")
        gui.setReadyState()
        return

    #pattern = re.compile("^\d{4}(-\d{2}){2} ([0-1][0-9]|[2][0-3]):([0-5][0-9])$")
    pattern = re.compile("^20\d{2}-((0[1-9])|(1[0-2]))-((0[1-9])|([1-2][0-9])|(3[0-1])) ([0-1][0-9]|[2][0-3]):([0-5][0-9])$")
    localDateFrom = gui.getDateFrom()
    localDateTo = gui.getDateTo()

    if pattern.match(localDateTo) is None:
        gui.setStatus("Please make sure date-from is in YYYY-mm-dd HH:MM format.")
        gui.setReadyState()
        return

    if pattern.match(localDateFrom) is None:
        gui.setStatus("Please make sure date-to is in YYYY-mm-dd HH:MM format.")
        gui.setReadyState()
        return


    try:
        global api
        api = VendApi(gui.getPrefix(), gui.getToken())


        objType = gui.getSelectedType()

        timezone = getTimeZone(api)

        if timezone is None:
            gui.setStatus("Please check prefix/token.")
            gui.setReadyState()
            return

        gui.setStatus("Converting time to UTC format...")
        #utcDateFrom = ControlUtil.getUtcTime(localDateFrom, START_DAY_TIME, timezone)
        #utcDateTo = ControlUtil.getUtcTime(localDateTo, END_DAY_TIME, timezone)
        utcDateFrom = ControlUtil.getUtcDateTime(localDateFrom, timezone)
        utcDateTo = ControlUtil.getUtcDateTime(localDateTo, timezone)

        gui.setStatus("Retrieving {0} for {1}...".format(objType, gui.getPrefix()))
        vendObjs = getVendObjects(api, utcDateFrom, utcDateTo, objType)

        #print(vendObjs)

        if vendObjs is None or len(vendObjs) == 0:
            gui.setStatus("There was nothing returned. Please check your dates.")
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

        addActionEvents(USER, APP_FUNCTION, objType, vendObjs)

        gui.setReadyState()

        if callback:
            kargs = {
                'prefix' : gui.getPrefix(),
                'token' : gui.getToken(),
                'ticketnum' : gui.getTicketNum(),
                'filepath' : filepath,
                'filename' : filename,
                'entity' : objType
            }

            callback(kwargs=kargs)
    except Exception as e:
        issue = GITAPI.createIssue(title=f"[{USER}]{str(e)}", body=traceback.format_exc(), assignees=['minstack'], labels=['bug']).json()

        if issue is not None and issue.get('html_url', None is not None):
            gui.setResult(f"Something went terribly wrong.\nDev notified and assigned to issue:\n{issue['html_url']}")
        else:
            gui.setResult(f"Something went terribly wrong.\nCould not notify dev.\n{traceback.format_exc()}")
        #print(traceback.format_exc())

def addActionEvents(user, app, type, results):

    details = f"Retrieved {type}:{len(results)},DateFrom:{gui.getDateFrom()},DateTo:{gui.getDateTo()}"

    toolusage.writeRow(**{
        "user" : user,
        "appfunction" : app,
        "completedon" : str(dt.now()),
        "prefix" : gui.getPrefix(),
        "ticketnum" : gui.getTicketNum(),
        "details" : details
    })

def exportToCsv(list, header, type):
    return CsvUtil.writeListToCSV(output=list, colHeader=header, title=type, prefix="")

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

    if objects is None or len(objects) == 0:
        return None

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

        print(oDate)
        if dFrom <= oDate <= dTo:
            filtered.append(o)

    return filtered

def getTimeZone(api):
    global outlets

    outlets = api.getOutlets()

    if outlets is None or len(outlets) == 0:
        return None

    outlet = getMostUpdatedOutlet(outlets)

    return outlet['time_zone']

def setToolUsageObject(tool):
    global toolusage

    toolusage = tool

def loadData(tool=None, git=None):

    global GITAPI
    global toolusage

    if tool is not None:
        toolusage = tool

    if git is not None:
        GITAPI = git
        return

    #for standalone for public with data to import
    #creds obviously not commited to repo
    try:
        with open('data.json') as f:
            data = json.load(f)
    except Exception:
        return


    ##print(f"{data['owner']}: {data['repo']} : {data['ghtoken']}")

    GITAPI = GitHubApi(owner=data['owner'], repo=data['repo'], token=data['ghtoken'])



    toolusage = ToolUsageSheets(credsfile=data['credjson'], \
                                sheetId=data['sheetId'], \
                                sheetName=USER)

def getMostUpdatedOutlet(outlets):

    maxVersion = 0
    maxOutlet = None

    for o in outlets:
        currVer = o['version']
        if  currVer > maxVersion:
            maxVersion = currVer
            maxOutlet = o


    return maxOutlet

if __name__ == '__main__':
    #gui should be here but I don't think this should ever be standalone as
    #the logic is meant to be in the gui to bulk delete right away
    loadData()
