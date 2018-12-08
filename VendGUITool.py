from VendBulkDeleteGUI import *
from VendGetGUI import *
from VendGUIToolGui import *
import VendBulkDelete as BulkDel






if __name__ == '__main__':
    tabTitles = ["Bulk Delete", "Retrieve"]
    mainGui = VendGUIToolGui(tabTitles)
    custDelGui = VendBulkDeleteGUI(BulkDel.startProcess, mainGui.tabs[tabTitles[0]])
    custGetGui = VendGetGUI(mainGui.tabs[tabTitles[1]])
    mainGui.main()
