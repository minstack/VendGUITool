from VendBulkDeleteGUI import *
from VendGetGUI import *
from VendGUIToolGui import *
import VendGet
import VendBulkDelete as BulkDel
from datetime import datetime as dt


def retrieveToDelete(kwargs):
    kwargs['gui'] = bulkDelGui
    BulkDel.deleteFromRetrieve(kwargs=kwargs)




if __name__ == '__main__':
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

    mainGui.main()
