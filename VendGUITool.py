from VendBulkCustomerDelGUI import *
from VendGetCustomersGUI import *
from VendGUIToolGui import *
import VendBulkCustomerDel as CustDel

tabTitles = ["Customer Delete", "Get Entity"]
mainGui = VendGUIToolGui(tabTitles)



custDelGui = VendBulkCustomerDelGUI(CustDel.startProcess, mainGui.tabs[tabTitles[0]])
custGetGui = VendGetCustomersGUI(mainGui.tabs[tabTitles[1]])
CustDel.gui = custDelGui
mainGui.main()
#root.mainloop()
