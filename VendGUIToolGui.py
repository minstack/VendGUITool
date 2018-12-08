from tkinter import *
from tkinter.ttk import *


class VendGUIToolGui:

    def __init__(self, tabTitles):

        self.root = Tk()
        self.root.geometry("700x500")
        self.root.title("Vend GUI Tool")
        self.root.call('tk', 'scaling', '2.0')
        self.note = Notebook(self.root)
        self.note.pack(fill=BOTH, expand=1)

        self.tabs = {}
        self.createTabs(tabTitles)

    def createTabs(self, tabTitles):

        for title in tabTitles:
            tempTab =  Frame(self.note)
            self.tabs[title] = tempTab
            self.note.add(tempTab, text=title)

    def main(self):
        self.root.mainloop()
