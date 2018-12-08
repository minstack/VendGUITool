from VendBulkDeleteGUI import *
from VendGetGUI import *
from VendGUIToolGui import *
import VendBulkDelete as CustDel

tabTitles = ["Customer Delete", "Get Entity"]
mainGui = VendGUIToolGui(tabTitles)



custDelGui = VendBulkDeleteGUI(CustDel.startProcess, mainGui.tabs[tabTitles[0]])
custGetGui = VendGetGUI(mainGui.tabs[tabTitles[1]])
CustDel.gui = custDelGui
mainGui.main()
#root.mainloop()
