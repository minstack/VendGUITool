
def addControl(mainArr, *controls):
    for c in controls:
        mainArr.append(c)

def setControlState(controls, state):
    for c in controls:
        c.config(state=state)

def clearTextBoxes(tboxes):
    for t in tboxes:
        t.delete(0, END)

def entriesHaveValues(tboxes):
    result = True

    for t in tboxes:
        result = eval('len(t.get().strip()) > 0 and result')

    return result
