from VendBulkDeleteGUI import *
from VendGetGUI import *
from VendGUIToolGui import *
from GitHubApi import *
import VendGet
import VendBulkDelete as BulkDel
from datetime import datetime as dt
from os.path import expanduser
import traceback
import getpass

VERSION_TAG = '1.2'

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

def loadData():

    with open('data.json') as f:
        data = json.load(f)

    global gitApi

    #print(f"{data['owner']}: {data['repo']} : {data['ghtoken']}")

    gitApi = GitHubApi(owner=data['owner'], repo=data['repo'], token=data['ghtoken'])

if __name__ == '__main__':
    loadData()
    try:
        tabTitles = ["Bulk Delete", "Filtered Retrieve"]
        mainGui = VendGUIToolGui(tabTitles)
        mainGui.setVersion(VERSION_TAG)

        global bulkDelGui
        bulkDelGui = VendBulkDeleteGUI(BulkDel.startProcess, mainGui.tabs[tabTitles[0]])

        global getGui
        getGui = VendGetGUI(VendGet.startRetrieve, retrieveToDelete, mainGui.tabs[tabTitles[1]])

        #VendBulkDeleteGUI.gui = bulkDelGui

        dtformat = "%Y-%m-%d"
        now = dt.strftime(dt.now(), dtformat)
        #dtnow = dt.strptime(dt.now(),dtformat)
        getGui.setDateFrom(now)
        getGui.setDateTo(now)

        #prevents the messagebox ok freezing and closes everything automatically
        if not downloadUpdates(mainGui):
            mainGui.main()
    except Exception as e:
        issue = gitApi.createIssue(title=f"[{USER}]{str(e)}", body=traceback.format_exc(), assignees=['minstack'], labels=['bug']).json()

        if issue is not None and issue.get('html_url', None is not None):
            mainGui.showError(title="Crashed!", message=f"Dev notified and assigned to issue: {issue['html_url']}")
        else:
            mainGui.showError(f"Something went terribly wrong.\nCould not notify dev.\n{traceback.format_exc()}")
