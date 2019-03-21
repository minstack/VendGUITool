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

VERSION_TAG = '1.1'

gitApi = GitHubApi(owner='minstack', repo='VendGUITool', token='')
USER = getpass.getuser()

def retrieveToDelete(kwargs):
    kwargs['gui'] = bulkDelGui
    BulkDel.deleteFromRetrieve(kwargs=kwargs)


def downloadUpdates(mainGui):


    latestrelease = gitApi.getLatestReleaseJson()

    tag = latestrelease.get('tag_name', None)

    #no releases
    if tag is None:
        return False

    if latestrelease['tag_name'] == VERSION_TAG:
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

if __name__ == '__main__':

    try:
        tabTitles = ["Bulk Delete", "Filtered Retrieve"]
        mainGui = VendGUIToolGui(tabTitles)

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
        mainGui.showError(title="Crashed!", message=f"Dev notified and assigned to issue: {issue['url']}")
