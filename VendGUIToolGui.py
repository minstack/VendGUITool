from tkinter import *
import tkinter.ttk as ttk
from tkinter import messagebox

class VendGUIToolGui:

    def __init__(self, tabTitles):

        self.root = Tk()
        self.root.geometry("700x500")
        self.title = "Vend GUI Tool"
        self.root.call('tk', 'scaling', '2.0')

        self.note = ttk.Notebook(self.root)
        self.note.pack(fill=BOTH, expand=1)

        self.tabs = {}
        self.createTabs(tabTitles)

        self.btnSubmitFeedback= Button(self.root, text="Submit Feedback", font="Helvetica 11")
        #self.btnSubmitFeedback.pack()
        self.btnSubmitFeedback.place(x=595, y=0)


    def createTabs(self, tabTitles):

        for title in tabTitles:
            tempTab =  Frame(self.note)
            self.tabs[title] = tempTab
            self.note.add(tempTab, text=title)

    def main(self):
        self.root.mainloop()

    def showMessageBox(self, title, message):
        messagebox.showinfo(title, message)

    def showError(self, title, message):
        messagebox.showerror(title, message)

    def setVersion(self, version):
        self.root.title(f"{self.title} v{version}")
