from VendBulkDeleteGUI import *
from VendGetGUI import *
from VendGUIToolGui import *
import VendGet
import VendBulkDelete as BulkDel
from datetime import datetime as dt






if __name__ == '__main__':
    tabTitles = ["Bulk Delete", "Retrieve"]
    mainGui = VendGUIToolGui(tabTitles)
    bulkDelGui = VendBulkDeleteGUI(BulkDel.startProcess, mainGui.tabs[tabTitles[0]])
    getGui = VendGetGUI(VendGet.start, mainGui.tabs[tabTitles[1]])

    dtformat = "%Y-%m-%d"
    now = dt.strftime(dt.now(), dtformat)
    #dtnow = dt.strptime(dt.now(),dtformat)
    getGui.setDateFrom(now)
    getGui.setDateTo(now)

    mainGui.main()
