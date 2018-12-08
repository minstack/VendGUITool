from tkinter import *
import threading
from tkinter.filedialog import askopenfilename
import ControlUtil
#from tkFileDialog import askopenfilename

class VendBulkDeleteGUI:

    def __init__(self, deletefunc, root=None):
        """
            Constructor for the GUI. The delete function passed is the entry
            function in the calling class/module to bind to the delete button.
        """
        self.TEXT_BOXES = []
        self.BUTTONS = []
        self.__deletefunc = deletefunc
        self.root = root
        if not self.root:
            self.root = Tk()
            self.root.geometry("700x500")
            self.root.call('tk','scaling', 2.0)
        #self.root.geometry("650x450")
            self.root.minsize(650,450)
        #self.root.resizable(0,0)
            self.root.title("Vend Bulk Customer Delete")
            self.root.pack_propagate(0)

        header = Label(self.root, text="Bulk Customer Delete", bd=1, font="San-Serif 18 bold", bg="#41B04B", fg="white")
        header.pack(side=TOP, anchor=W, fill=X)

        # container for the main widgets
        mainFrame = Frame(self.root)


        self.__loadUserInputs__(mainFrame)
        self.__loadButtons__(mainFrame)
        self.__loadCsvControl__(mainFrame)
        self.__loadCheckListControl__(mainFrame)
        self.__loadMessageControls__(mainFrame)
        mainFrame.pack(padx=30, pady=10, fill=BOTH, expand=1)


    def __loadUserInputs__(self, mainFrame):
        """
            Loads the user input controls onto the given parent frame
        """
        lblStorePrefix = Label(mainFrame, text="Store Prefix:", font="Helvetica 14 bold")
        lblStorePrefix.grid(row=1, column=0, sticky=E)

        lblToken = Label(mainFrame, text="Token:", font="Helvetica 14 bold")
        lblToken.grid(row=2, column=0, sticky=E)

        lblCsv = Label(mainFrame, text="CSV File:", font="Helvetica 14 bold")
        #lblCsv.grid(row=3, column=0, sticky=E)

        #textboxes
        self.txtPrefix = Entry(mainFrame)
        self.txtToken = Entry(mainFrame)
        self.txtPrefix.grid(row=1,column=1, sticky=W)
        self.txtToken.grid(row=2,column=1, sticky=W)

        ControlUtil.addControl(self.TEXT_BOXES, self.txtPrefix, self.txtToken)

    def __loadButtons__(self, mainFrame):
        """
            Loads the button controls onto the given parent frame
        """
        btnframe = Frame(mainFrame)
        self.btnDelCust = Button(btnframe, text="Delete Customers", command=self.startThread)
        self.btnDelCust.pack(side=RIGHT, padx=5)
        self.btnReset = Button(btnframe, text="Reset", command=self.reset)
        self.btnReset.pack()
        btnframe.grid(row=5, column=1, padx=5, pady=10)

        radioFrame = Frame(mainFrame)
        radioFrame.grid(row=4, column=1)

        self.entityType = StringVar()
        custRadio = Radiobutton(radioFrame, text="Customer", value='Customers', variable=self.entityType, command=self.__switchEntityType)
        custRadio.invoke()
        custRadio.pack(side=LEFT)
        temp = Radiobutton(radioFrame, text="Products", value='Products', variable=self.entityType, command=self.__switchEntityType)
        temp.configure(state=DISABLED)
        temp.pack()

        ControlUtil.addControl(self.BUTTONS, self.btnDelCust, self.btnReset)

    def __loadCsvControl__(self, mainFrame):
        """
            Loads the CSV file controls onto the given parent frame
        """
        self.csvList = []
        self.csvFileDict = {}
        self.csvListbox = Listbox(mainFrame, listvariable=self.csvList, width=25, bd=0.5, selectmode='single')


        #csvHeader.grid(row=0, column=2)
        self.csvListbox.grid(row=1, column=2, rowspan=3, padx=10, pady=5)

        csvFrame = Frame(mainFrame, padx=10)

        csvHeader = Label(csvFrame, text="CSV Files", font="Helvetica 14 bold")
        csvHeader.pack(side=LEFT)

        csvFrame.grid(row=4, column=2, sticky=E)
        self.btnOpenCsvDialog = Button(csvFrame, text="+", font="Helvetica 14 bold", command=self.openFile, width=3)
        self.btnOpenCsvDialog.pack(side=LEFT)
        self.btnDeleteFile = Button(csvFrame, text="-", font="Helvetica 14 bold", command=self.deleteFileFromList, width=3)
        self.btnDeleteFile.pack()

        ControlUtil.addControl(self.BUTTONS, self.btnOpenCsvDialog, self.btnDeleteFile)

    def __loadCheckListControl__(self, mainFrame):
        """
            Loads the check list controls onto the given parent frame
        """
        checklistFrame = Frame(mainFrame, width=200, height=200, bd=1)
        #Label(mainFrame, text="Checklist", font="Helvetica 14 bold").grid(row=0, column=3)
        checklistFrame.grid(row=3, column=1)

        self.paConfirmation = BooleanVar()
        self.tokenExpiry = BooleanVar()
        self.chkPaConfirm = Checkbutton(checklistFrame, text="PA Confirmation", variable=self.paConfirmation)
        self.chkPaConfirm.grid(row=1, sticky=W)
        self.chkTokenExpiry = Checkbutton(checklistFrame, text="Token Expiry Set", variable=self.tokenExpiry)
        self.chkTokenExpiry.grid(row=2, sticky=W)

        ControlUtil.addControl(self.BUTTONS, self.chkPaConfirm, self.chkTokenExpiry)

    def __loadMessageControls__(self, mainFrame):
        """
            Loads the status/result message controls onto the given parent frame
        """
        self.statusMsg = StringVar()
        self.lblStatus = Label(self.root, textvariable=self.statusMsg, bd=1, relief=SUNKEN, anchor=W, bg="#3A4953", fg="white", font="Helvetica 14 italic")
        self.lblStatus.pack(side=BOTTOM, fill=X)

        resultFrame = Frame(mainFrame)
        resultFrame.grid(row=6,column=0, columnspan=3, rowspan=4)

        self.resultText = StringVar()
        resultLabel = Message(resultFrame, textvariable=self.resultText,font="Helvetica 16", width=500)
        resultLabel.pack(pady=15)

    def __switchEntityType(self):
        self.btnDelCust.config(text="Delete {0}".format(self.entityType.get()))
        # switch the process function

    def reset(self):
        """
            Function to reset the state of the GUI.
        """
        self.setStatus("")
        self.setReadyState()
        ControlUtil.clearTextBoxes(self.TEXT_BOXES)
        self.paConfirmation.set(0)
        self.tokenExpiry.set(0)
        del self.csvList[:]
        self.csvListbox.delete(0,END)
        self.csvFileDict = {}
        self.setResult("")

    def deleteFileFromList(self):
        """
            Function to delete the selected file from the CSV listbox as well
            as the corresponding list variable and dictionary.
        """
        selected = self.csvListbox.curselection()

        if selected:
            self.csvListbox.delete(selected[0])
            self.csvFileDict.pop(self.csvList[selected[0]], None)
            del self.csvList[selected[0]]

    def entriesHaveValues(self):
        """
            Returns true/false whether the required input values have been
            provided
        """
        return ControlUtil.entriesHaveValues(self.TEXT_BOXES) and (len(self.csvList) > 0)

    def startThread(self):
        """
            Main function to start the thread to the provided function of the
            controller that creates/calls this class.
        """
        self.setStatus("")
        self.setDeletingState()
        thr = threading.Thread(target=self.__deletefunc, args=([self]), kwargs={})

        thr.start()
        #self.setReadyState()

    def isChecklistReady(self):
        """ Returns whether the checklist is completed. """
        return self.tokenExpiry.get() and self.paConfirmation.get()

    def openFile(self):
        """
            When the + button is clicked to add CSV files, opens the file opener
            dialog to retrieve the file.
        """
        filepath = askopenfilename(parent=self.root)

        if filepath:
            tempArr = filepath.split("/")

            filename = tempArr[len(tempArr)-1]

            if self.csvFileDict.get(filename, None) is not None:
                self.setStatus("{0} has been added already.".format(filename))
                return

            self.csvFileDict[filename] = filepath
            self.csvList.append(filename)

            self.csvListbox.insert(END, filename)


    def setStatus(self, msg):
        """ Sets the status message to the provided string. """
        self.statusMsg.set(msg)

    def setResult(self, msg):
        """ Sets the result variable to the given string. """
        self.resultText.set(msg)

    def setDeletingState(self):
        """ Sets all the controls to disabled state to prevent any multi-clicks"""
        self.btnReset.config(state=DISABLED)
        self.btnDelCust.config(state=DISABLED)
        self.btnOpenCsvDialog.config(state=DISABLED)
        self.btnDeleteFile.config(state=DISABLED)
        self.txtToken.config(state=DISABLED)
        self.txtPrefix.config(state=DISABLED)
        self.chkPaConfirm.config(state=DISABLED)
        self.chkTokenExpiry.config(state=DISABLED)
        self.root.update()

    def setReadyState(self):
        """ Resets all controls back to normal state."""
        self.btnReset.config(state=NORMAL)
        self.btnDelCust.config(state=NORMAL)
        self.btnOpenCsvDialog.config(state=NORMAL)
        self.btnDeleteFile.config(state=NORMAL)
        self.txtToken.config(state=NORMAL)
        self.txtPrefix.config(state=NORMAL)
        self.chkPaConfirm.config(state=NORMAL)
        self.chkTokenExpiry.config(state=NORMAL)
        self.root.update()

    def setDeletingState(self):
        """ Sets all the controls to disabled state to prevent any multi-clicks"""
        self.__setControlState(self.TEXT_BOXES, DISABLED)
        self.__setControlState(self.BUTTONS, DISABLED)
        self.root.update()

    def setReadyState(self):
        """ Resets all controls back to normal state."""

        self.__setControlState(self.TEXT_BOXES, NORMAL)
        self.__setControlState(self.BUTTONS, NORMAL)
        self.root.update()

    def __setControlState(self, controls, state):
        for c in controls:
            c.config(state=state)

    def main(self):
        """ Main loop for this GUI. """
        self.root.mainloop()
