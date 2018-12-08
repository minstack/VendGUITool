from tkinter import *
import threading
from tkinter.filedialog import askopenfilename
#from tkFileDialog import askopenfilename

class VendGetGUI:

    def __init__(self, root=None):
        """
            Constructor for the GUI. The delete function passed is the entry
            function in the calling class/module to bind to the delete button.
        """

        self.root = root
        if not self.root:
            self.root = Tk()
            self.root.geometry("700x500")
            self.root.call('tk','scaling', 2.0)
        #self.root.geometry("650x450")
            self.root.minsize(650,450)
        #self.root.resizable(0,0)
            self.root.title("Vend Get Entity")
            self.root.pack_propagate(0)
        header = Label(self.root, text="Get Entity", bd=1, font="San-Serif 18 bold", bg="#41B04B", fg="white")
        header.pack(side=TOP, anchor=W, fill=X)

        # container for the main widgets
        mainFrame = Frame(self.root)


        self.__loadUserInputs__(mainFrame)
        self.__loadButtons__(mainFrame)
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
        self.txtPrefix.grid(row=1,column=1, sticky=W, pady=5)
        self.txtToken.grid(row=2,column=1, sticky=W, pady=5)

        lblDateFrom = Label(mainFrame, text="Date From:", font="Helvetica 14 bold")
        lblDateFrom.grid(row=3, column=0, sticky=E)
        lblDateTo = Label(mainFrame, text="Date To:", font="Helvetica 14 bold")
        lblDateTo.grid(row=4, column=0, sticky=E)

        self.txtDateFrom = Entry(mainFrame)
        self.txtDateTo = Entry(mainFrame)
        self.txtDateFrom.grid(row=3,column=1, sticky=W, pady=5)
        self.txtDateTo.grid(row=4,column=1, sticky=W, pady=5)

    def __loadButtons__(self, mainFrame):
        """
            Loads the button controls onto the given parent frame
        """
        btnframe = Frame(mainFrame)
        self.btnDelCust = Button(btnframe, text="Delete Customers", command=self.startThread)
        self.btnDelCust.pack(side=RIGHT, padx=5)
        self.btnReset = Button(btnframe, text="Reset", command=self.reset)
        self.btnReset.pack()
        btnframe.grid(row=6, column=1, padx=10)

        radioFrame = Frame(mainFrame)

        self.entityType = StringVar()

        Label(radioFrame, text='Type', font="Helvetica 16 bold").pack()

        Radiobutton(radioFrame, text="Customers", variable=self.entityType, value='customers', font="Helvetica 14").pack(anchor=W, pady=5)
        Radiobutton(radioFrame, text="Products", variable=self.entityType, value='products', font="Helvetica 14").pack(anchor=W, pady=5)

        temp = Radiobutton(radioFrame, text="Sales", variable=self.entityType, value='sales', font="Helvetica 14")
        temp.configure(state=DISABLED)
        temp.pack(anchor=W, pady=5)

        radioFrame.grid(row=0, column=3, rowspan=4, padx=20, sticky=N)

    def __loadMessageControls__(self, mainFrame):
        """
            Loads the status/result message controls onto the given parent frame
        """
        self.statusMsg = StringVar()
        self.lblStatus = Label(self.root, textvariable=self.statusMsg, bd=1, relief=SUNKEN, anchor=W, bg="#3A4953", fg="white", font="Helvetica 14 italic")
        self.lblStatus.pack(side=BOTTOM, fill=X)

        resultFrame = Frame(mainFrame)
        resultFrame.grid(row=7,column=0, columnspan=3, rowspan=4)

        self.resultText = StringVar()
        resultLabel = Message(resultFrame, textvariable=self.resultText,font="Helvetica 16", width=500)
        resultLabel.pack(pady=15)

    def reset(self):
        """
            Function to reset the state of the GUI.
        """
        self.setStatus("")
        self.setReadyState()
        self.txtToken.delete(0,END)
        self.txtPrefix.delete(0,END)
        self.paConfirmation.set(0)
        self.tokenExpiry.set(0)
        del self.csvList[:]
        self.csvListbox.delete(0,END)
        self.csvFileDict = {}
        self.setResult("")

    def entriesHaveValues(self):
        """
            Returns true/false whether the required input values have been
            provided
        """
        return (len(self.txtPrefix.get().strip()) > 0) and (len(self.txtToken.get().strip()) > 0)

    def startThread(self):
        """
            Main function to start the thread to the provided function of the
            controller that creates/calls this class.
        """
        self.setStatus("")
        self.setDeletingState()
        thr = threading.Thread(target=self.__deletefunc, args=(), kwargs={})

        thr.start()
        #self.setReadyState()

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

    def main(self):
        """ Main loop for this GUI. """
        self.root.mainloop()
