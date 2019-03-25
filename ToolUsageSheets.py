import requests, json
import gspread as gs
from oauth2client.service_account import ServiceAccountCredentials


class ToolUsageSheets:

    scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']


    NEXT_ROW_CELL = ''
    ROW_RANGE = 'A{0}:F{1}'
    LOCAL_ROWS = []


    def __init__(self, credsfile, sheetId, sheetName, nextrowcell='K1'):
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(credsfile, self.scope)
        self.gc = gs.authorize(self.credentials)
        #self.sheet = self.gc.open_by_key(sheetId).worksheet(sheetName)
        self.sheet = self.gc.open_by_key(sheetId).worksheet(sheetName)
        self.NEXT_ROW_CELL = nextrowcell

    def writeRow(self, user, appfunction, completedon, prefix, ticketnum, details):
        rowNumToWrite = self.getNextRow()
        self.incrementNextRowVal()

        ztick = f"https://vendhelp.zendesk.com/agent/tickets/{ticketnum}"

        rowToWrite = [completedon, user, appfunction, prefix, ztick, details]
        range = self.ROW_RANGE.format(rowNumToWrite, rowNumToWrite)

        cell_list = self.sheet.range(range)

        i = 0
        for cell in cell_list:
            cell.value = rowToWrite[i]
            i+=1
            print(cell.value)

        print(cell_list)
        self.sheet.update_cells(cell_list)


    def getNextRow(self):
        return self.sheet.acell(self.NEXT_ROW_CELL).value

    def incrementNextRowVal(self, increment=1):
        curr = int(self.getNextRow())

        self.sheet.update_acell(self.NEXT_ROW_CELL, curr+increment)

    def saveRowLocally(self, user, appfunction, completedon, prefix, ticketnum, details):
        self.LOCAL_ROWS.append(
            {
                "user" : user,
                "appfunction" : appfunction,
                "completedon" : completedon,
                "prefix" : prefix,
                "ticketnum" : ticketnum,
                "details" : details
            }
        )

    def writeLocallySavedRows(self):
        rCount = len(self.LOCAL_ROWS)

        if rCount == 0:
            return

        if rCount > 1:
            self.batchUpdate(self.LOCAL_ROWS)
            return


        self.writeRow(**self.LOCAL_ROWS[0])


    def batchUpdate(self, rowsObjs):
        rowToWrite = int(self.getNextRow())
        rCount = len(rowsObjs)

        self.incrementNextRowVal(rCount)
        rowsList = self.getObjToLists(rowsObjs)

        print(rowsList)

        for row in rowsList:
            print(rowToWrite, row)

            range = self.ROW_RANGE.format(rowToWrite, rowToWrite)
            cell_list = self.sheet.range(range)



            i = 0

            for cell in cell_list:
                cell.value = row[i]
                i+=1


            self.sheet.update_cells(cell_list)

            rowToWrite += 1



    def getObjToLists(self, objs):

        rows = []

        for o in objs:

            rows.append([o['completedon'],\
                 o['user'],\
                 o['appfunction'],\
                 o['prefix'],\
                 f"https://vendhelp.zendesk.com/agent/tickets/{o['ticketnum']}"],\
                 o['details'])
            '''
            rows.append(o['user'])
            rows.append(o['appfunction'])
            rows.append(o['completedon'])
            rows.append(o['prefix'])
            rows.append(f"https://vendhelp.zendesk.com/agent/tickets/{o['ticketnum']}")
                '''
        return rows


    '''
    def dumpDataToSheets(self, data):

        scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']

        credentials = ServiceAccountCredentials.from_json_keyfile_name(CONFIGS['api_credential_filename'], scope)
        #credentials = ServiceAccountCredentials.from_json_keyfile_name(apiCredentialPath, scope)

        gc = gs.authorize(credentials)


        sheet = gc.open_by_key(CONFIGS['sheetId']).sheet1

        clearSheet(sheet)

        i = 0
        for item in data:
            headers = data[item]['headers']

            sheet.update_cell(1, i+1, headers[0])
            sheet.update_cell(1, i+2, headers[1])

            agents = data[item][headers[0]]
            nums = data[item][headers[1]]

            for j, dItem in enumerate(agents):
                sheet.update_cell(j + 2, i + 1, agents[j])
                sheet.update_cell(j + 2, i + 2, nums[j])

            i += 2
        '''
