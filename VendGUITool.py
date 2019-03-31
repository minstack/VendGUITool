from VendBulkDeleteGUI import *
from VendGetGUI import *
from VendGUIToolGui import *
from VendFixAvgCostGUI import *
from GitHubApi import *
import VendFixAvgCost as fixavgcost
import VendBulkDelete as BulkDel
import VendGet as vendget
from datetime import datetime as dt
from os.path import expanduser
import traceback
import getpass
import GitFeedbackIssue as gitfeedback

VERSION_TAG = '1.3'

USER = getpass.getuser()

def retrieveToDelete(kwargs):
    kwargs['gui'] = bulkDelGui
    BulkDel.deleteFromRetrieve(kwargs=kwargs)


def downloadUpdates(mainGui):


    latestrelease = gitApi.getLatestReleaseJson()

    tag = latestrelease.get('tag_name', None)

    #print(tag, latestrelease['tag_name'])

    #no releases
    if tag is None:
        return False

    if latestrelease['tag_name'] <= VERSION_TAG:
        return False

    #download latest update
    userdesktop = expanduser('~') + '/Desktop'
    filename = gitApi.downloadLatestRelease(path=userdesktop, extract=True)
    updatedescription = latestrelease['body']

    mainGui.showMessageBox(title=f"Updates v{latestrelease['tag_name']}", \
                            message=f"Downloaded latest version to your desktop: \
                                        {filename[:-4]}\n\nYou may delete this version.\
                                        \n\nUpdate Details:\n{updatedescription}")

    return True

def loadData(tool=None, git=None):

    global gitApi
    global toolusage

    if tool is not None:
        toolusage = tool

    if git is not None:
        gitApi = git
        return

    #for standalone for public with data to import
    #creds obviously not commited to repo
    try:
        with open('data.json') as f:
            data = json.load(f)
    except Exception:
        return




    ##print(f"{data['owner']}: {data['repo']} : {data['ghtoken']}")

    gitApi = GitHubApi(owner=data['owner'], repo=data['repo'], token=data['ghtoken'])



    toolusage = ToolUsageSheets(credsfile=data['credjson'], \
                                sheetId=data['sheetId'], \
                                sheetName=USER)

def setToolAndGitToControllers():

    vendget.loadData(tool=toolusage, git=gitApi)
    BulkDel.loadData(tool=toolusage, git=gitApi)
    fixavgcost.loadData(tool=toolusage, git=gitApi)


def setToolsObjs():
    VendGet.setToolUsageObject(toolusage)
    BulkDel.setToolUsageObject(toolusage)

def openFeedbackDialog():
    gitfeedback.main()

import VendGet

if __name__ == '__main__':
    loadData()
    #setToolsObjs()
    try:
        tabTitles = ["Bulk Delete", "Filtered Retrieve", "Fix Avg Cost"]
        mainGui = VendGUIToolGui(tabTitles)
        mainGui.setVersion(VERSION_TAG)

        global bulkDelGui
        bulkDelGui = VendBulkDeleteGUI(BulkDel.startProcess, mainGui.tabs[tabTitles[0]])

        global getGui
        getGui = VendGetGUI(VendGet.startRetrieve, retrieveToDelete, mainGui.tabs[tabTitles[1]])

        global facGui
        facGui = VendFixAvgCostGUI(fixavgcost.startProcess, mainGui.tabs[tabTitles[2]])
        fixavgcost.setGlobalGui(facGui)
        #VendBulkDeleteGUI.gui = bulkDelGui

        dtformat = "%Y-%m-%d %H:%M"
        now = dt.strftime(dt.now(), dtformat)
        #dtnow = dt.strptime(dt.now(),dtformat)
        getGui.setDateFrom(now)
        getGui.setDateTo(now)

        setToolAndGitToControllers()

        #prevents the messagebox ok freezing and closes everything automatically
        if not downloadUpdates(mainGui):
            mainGui.setFeedbackCommand(openFeedbackDialog)
            mainGui.main()
    except Exception as e:
        issue = gitApi.createIssue(title=f"[{USER}]{str(e)}", body=traceback.format_exc(), assignees=['minstack'], labels=['bug']).json()

        if issue is not None and issue.get('html_url', None is not None):
            mainGui.showError(title="Crashed!", message=f"Dev notified and assigned to issue: {issue['html_url']}")
        else:
            mainGui.showError(f"Something went terribly wrong.\nCould not notify dev.\n{traceback.format_exc()}")
