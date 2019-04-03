import csv
from VendApi import *
from VendFixAvgCostGUI import *
from GitHubApi import *
import re
import threading
import queue
import tkinter
import CsvUtil
import traceback
import os
import time
import getpass
from datetime import datetime

gui = None
api = None
retrieveFilepath = ""
THREAD_COUNT = 1

USER = getpass.getuser()
APP_FUNCTION = "VendFixAvgCost"

def startProcess(bulkDelGui):
    """
        The entry point to begin retrieving customers to delete and process the
        bulk delete task. Handles all the basic error checks and feedback to the
        user through the GUI status message/bar, before creating API class.
    """
    global gui
    gui = bulkDelGui

    checkEntries()
    '''
    gui.setStatus("")
    if not gui.entriesHaveValues():
        ## error
        gui.setStatus("Please have values for prefix, token and CSV.")
        gui.setReadyState()
        return

    if not gui.isChecklistReady():
        gui.setStatus("Please make sure checklist is completed.")
        gui.setReadyState()
        return'''

    pattern = re.compile("^.+[.]csv$", re.IGNORECASE)

    for file in gui.csvList:
        if pattern.match(file) is None:
            gui.setStatus("Please make sure the selected files are .csv file.")
            gui.setReadyState()
            return

    global api
    try:
        api = VendApi(gui.txtPrefix.get().strip(), gui.txtToken.get().strip())

        #Retrieval
        outlets = api.getOutlets()

        if not api.connectSuccessful(outlets):
            gui.setStatus("Please make sure prefix/token are correct (expiry).")
            gui.setReadyState()
            return

        prodsIdtofix = getCsvProdsToFix()

        if len(prodsIdtofix) == 0:
            gui.setStatus("Please make sure CSV has an 'id' column.")
            gui.setReadyState()
            return


        gui.setStatus("Retrieving products...")
        fullProdList = api.getProducts(endpointVersion='0.9')

        prodIdtoProdObj = getProdIdtoObj(fullProdList)
        prodIdtoInventory = getProdIdToInventory(prodsIdtofix, prodIdtoProdObj)

        gui.setStatus("Zeroing out inventory...")
        #Zero out inventory
        zeroOutInventory(prodIdtoInventory, api)

        #Proccess Stock stockorders
        gui.setStatus("Creating stock orders...")
        consignments = createStockOrders(api, outlets)

        gui.setStatus("Receiving consignment products...")
        negativeProds = addConsignmentProducts(api, consignments, prodIdtoInventory)

        receiveConsignments(consignments)
        #Cleanup with original inventory <=0
        gui.setStatus("Restoring originally negative/zero inventory products...")
        cleanupNegativeInventory(api, negativeProds)

        addActionEvents(user=USER, app=APP_FUNCTION, date=str(datetime.now()), numfixed=len(prodsIdtofix))
        gui.setStatus("Done.")
        gui.setReadyState()

    except Exception as e:
        issue = GITAPI.createIssue(title=f"[{USER}]{str(e)}", body=traceback.format_exc(), assignees=['minstack'], labels=['bug']).json()
        #issue = None
        if issue is not None and issue.get('html_url', None is not None):
            gui.showError(title="Crashed!", message=f"Something went terribly wrong.\nDev notified and assigned to issue:\n{issue['html_url']}")
        else:
            gui.showError(title="Crashed!", message=f"Something went terribly wrong.\nCould not notify dev.\n{traceback.format_exc()}")

def checkEntries():


    gui.setStatus("")
    if not gui.entriesHaveValues():
        ## error
        gui.setStatus("Please have values for prefix, token, ticket # and CSV.")
        gui.setReadyState()
        return

    if not gui.isChecklistReady():
        gui.setStatus("Please make sure checklist is completed.")
        gui.setReadyState()
        return

def getAllMismatchedCost():

    gui.setStatus("")
    if not gui.entriesHaveValuesNoCsv():
        ## error
        gui.setStatus("Please have values for prefix, token and ticket #.")
        gui.setReadyState()
        return

    if not gui.isChecklistReady():
        gui.setStatus("Please make sure checklist is completed.")
        gui.setReadyState()
        return

    try:
        api = VendApi(gui.txtPrefix.get().strip(), gui.txtToken.get().strip())

        #Retrieval
        outlets = api.getOutlets()

        if not api.connectSuccessful(outlets):
            gui.setStatus("Please make sure prefix/token are correct (expiry).")
            gui.setReadyState()
            return

        gui.setStatus("Retrieving inventory records...")
        inventories = api.getInventories()

        print(f'in fixavgcost inventories: {len(inventories)}')
        prodidtoinv = getPidToInventory(inventories)

        #print(inventories)

        gui.setStatus("Retrieving products...")
        #prods = api.getProducts()
        prods = api.getProducts2() #something weird is goig on with api.getProducts() returning only 1 product
        #print(f"prods var: {len(prods)}")
        # pidtoobj = api.getKeyToObjs(prods, 'id')
        # print(f'{len(pidtoobj)} - pidtoobj')
        #added sku,name,handle as well
        prodid_cost = getProdIdAndCost(prods)



        #JsonUtil.writeJsonToFile(products, 'products.json')

        #print(products)
        gui.setStatus("Finding mismatched supply_price - avg cost...")
        # list of {'prod_id': id, 'supply_price' : supply_price, 'average_cost'}
        mismatchedAndNoInvProds = getMismatchedProds(prodid_cost, prodidtoinv)
        mismatchedProds = mismatchedAndNoInvProds['mismatched']
        noinvprods = mismatchedAndNoInvProds['no_inventory_record']
        # JsonUtil.writeJsonToFile(filename='prodidtoinv.json', data=prodidtoinv)
        # JsonUtil.writeJsonToFile(filename='prodid_cost.json', data=prodid_cost)

        print(f'mis: {len(mismatchedProds)}, noinv: {len(noinvprods)}')
        if len(mismatchedProds) > 0:
            gui.setStatus(f"Found {len(mismatchedProds)} mismatched products...exporting CSV...")
            # exportFormat = getMismatchedToExport(mismatchedProds, pidtoobj)
            exportFormat = getMismatchedToExport(mismatchedProds)

            filepath = exportToCSV(exportFormat)

            gui.setStatus(f"Exported CSV to {filepath}.")

        addActionEvents(user=USER, app=APP_FUNCTION, date=str(datetime.now()), numfixed=len(mismatchedProds))
        gui.setStatus("Done.")
        gui.setReadyState()

    except Exception as e:
        issue = GITAPI.createIssue(title=f"[{USER}]{str(e)}", body=traceback.format_exc(), assignees=['minstack'], labels=['bug']).json()
        #issue = None
        if issue is not None and issue.get('html_url', None is not None):
            gui.showError(title="Crashed!", message=f"Something went terribly wrong.\nDev notified and assigned to issue:\n{issue['html_url']}")
        else:
            gui.showError(title="Crashed!", message=f"Something went terribly wrong.\nCould not notify dev.\n{traceback.format_exc()}")

def exportToCSV(exportFormat):

    #print(exportFormat)

    ids = exportFormat['id']
    skus = exportFormat['sku']
    handles = exportFormat['handle']
    names = exportFormat['name']
    supprices = exportFormat['supply_price']
    avgcosts = exportFormat['average_cost']

    zipped = zip(ids, skus, handles, names, supprices, avgcosts)

    return CsvUtil.writeListToCSV(output=zipped, prefix=gui.getPrefix(), title="mismatchedcosts")



def getMismatchedToExport(mismatched, pidtoobj=None):
    exportready = {
        'id' : [],
        'sku' : [],
        'handle' : [],
        'name' : [],
        'supply_price' : [],
        'average_cost' : []
    }

    #JsonUtil.writeJsonToFile(filename='pidtoobjexport.json', data=pidtoobj)

    for m in mismatched:
        pid = m['prod_id']
        supprice = m['supply_price']
        avgcost = m['average_cost']
        sku = m['sku']
        handle = m['handle']
        name = m['name']

        # if pidtoobj.get(pid, None) is None:
        #     #print(pid)
        #     continue

        # sku = pidtoobj[pid]['sku']
        # handle = pidtoobj[pid]['handle']
        # name = pidtoobj[pid]['name']


        exportready['id'].append(pid)
        exportready['sku'].append(sku)
        exportready['handle'].append(handle)
        exportready['name'].append(name)
        exportready['supply_price'].append(supprice)
        exportready['average_cost'].append(avgcost)

    return formatExportHeaders(exportready)


def formatExportHeaders(export):

    for l in export:
        export[l].insert(0, l)

    return export


def getMismatchedProds(pidcost, pidtoinv):

    mismatched = []
    #print(pidtoinv)

    #JsonUtil.writeJsonToFile(pidcost, 'pidcost.json')
    #JsonUtil.writeJsonToFile(pidtoinv, 'pidtoinv.json')
    noinv = []
    for pc in pidcost:
        pid = pc['prod_id']
        cost = float(pc['cost'])

        prodinvs = pidtoinv.get(pid, None)

        if prodinvs is None:
            #print(f'no inventories: {pid}')
            noinv.append(pc)
            continue

        for i in prodinvs:
            curravgcost = float(i['average_cost'])

            if curravgcost != cost:
                #print(f"avgcost: {curravgcost}, supply_price: {cost}")
                mismatched.append(
                    {
                        'prod_id' : pid,
                        'supply_price' : cost,
                        'average_cost' : curravgcost,
                        'sku' : pc['sku'],
                        'handle' : pc['handle'],
                        'name' : pc['name']
                    }
                )
                break

    print(f'mismatched list: {len(mismatched)}\n')

    return {'mismatched' : mismatched, 'no_inventory_record' : noinv}


def getProdIdAndCost(prods):
    pidandcost = []
    #JsonUtil.writeJsonToFile(prods, 'prods.json')
    #print(prods)
    for p in prods:
        pid = p['id']
        cost = p['supply_price']
        sku = p['sku']
        handle = p['handle']
        name = p['name']

        pidandcost.append(
            {
                'prod_id' : pid,
                'cost' : cost,
                'name' : name,
                'sku' : sku,
                'handle' : handle
            }
        )

    return pidandcost

def receiveConsignments(consignments):

    for c in consignments:

        api.updateConsignment(c)

def cleanupNegativeInventory(api, negprodsinv):

    #print(negprodsinv)

    for p in negprodsinv:

        #print(p)

        prodid = p['product_id']
        inv = p['inventory']

        response = api.updateProductInventory(prodid, [inv])

        #print(response.json())

def addConsignmentProducts(api, consignments, prodIdToInventory):

    negativeProds = []

    outletToConsignment = getOutletIdToConsignment(consignments)
    #pidtoOutletInventory = getProdIdToOutletInventory(prodIdToInventory)

    inventorieswithpid = getInventoryWithPid(prodIdToInventory)

    i = 0
    while i < len(inventorieswithpid):
        oid = inventorieswithpid[i]['outlet_id']
        pid = inventorieswithpid[i]['product_id']
        supply_price = inventorieswithpid[i]['cost']
        qty = float(inventorieswithpid[i]['count'])

        print(inventorieswithpid[i])

        if qty <= 0:
            qty = 1
            negativeProds.append(
                {
                    "product_id" : pid,
                    "inventory" : inventorieswithpid[i]
                }
            )

        consignmentId = outletToConsignment[oid]['id']

        gui.setStatus(f"Adding product to consignment {outletToConsignment[oid]['name']} - qty:{qty}, supply price:{supply_price}...")

        response = api.addConsignmentProductReceived(consignmentId, pid, qty, supply_price)

        if response.status_code == 429:
            gui.setStatus("Rate Limited while adding consignment product. Will continue after 5 minutes...")
            print("rate limited at addConsignmentProductsReceived")
            time.sleep(301)
            continue

        i+=1

    return negativeProds
    '''
    for inv in inventorieswithpid:
        oid = inv['outlet_id']
        pid = inv['product_id']
        supply_price = inv['cost']
        qty = inv['count']

        consignmentId = outletToConsignment[oid]['id']

        gui.setStatus(f"Adding {pid} to consignment {consignmentId} - qty:{qty}, supply price:{supply_price}...")

        response = api.addConsignmentProductReceived(consignmentId, pid, qty, supply_price)

        if response.status_code == 429:
            gui.setStatus("Rate Limited while adding consignment product. Will continue after 5 minutes...")
            print("rate limited at addConsignmentProductsReceived")
            time.sleep(301)
            response = api.addConsignmentProductReceived(consignmentId, pid, qty, supply_price)

    for oid in outletToConsignment:

        for i in inventorieswithpid:
            pid = i['product_id']
            inventories = prodIdToInventory[pid]['inventory']
            supply_price = prodIdToInventory[pid]['cost']

            for i in inventories:
                if i['outlet_id'] == oid:
                    qty = float(i['count'])

                    if qty <= 0:
                        qty = 1
                        negativeProds.append(
                            {
                                "product_id" : pid,
                                "inventory" : i
                            }
                        )

                    consignmentId = outletToConsignment[oid]['id']

                    response = api.addConsignmentProductReceived(consignmentId, pid, qty, supply_price)
                    gui.setStatus(f"Added {pid} to consignment {consignmentId} - qty:{qty}, supply price:{supply_price}...")
                    if response.status_code == 429:
                        gui.setStatus("Rate Limited while adding consignment product. Will continue after 5 minutes...")
                        print("rate limited at addConsignmentProductsReceived")
                        time.sleep(301)
                        response = api.addConsignmentProductReceived(consignmentId, pid, qty, supply_price)

    #this is quite ridiculous o(n^3) I don't think i've ever coded
    #need to use my brain more to figure this out
    for oid in outletToConsignment:

        for pid in prodIdToInventory:
            inventories = prodIdToInventory[pid]['inventory']
            supply_price = prodIdToInventory[pid]['cost']

            for i in inventories:
                if i['outlet_id'] == oid:
                    qty = float(i['count'])

                    if qty <= 0:
                        qty = 1
                        negativeProds.append(
                            {
                                "product_id" : pid,
                                "inventory" : i
                            }
                        )

                    consignmentId = outletToConsignment[oid]['id']

                    response = api.addConsignmentProductReceived(consignmentId, pid, qty, supply_price)
                    gui.setStatus(f"Added {pid} to consignment {consignmentId} - qty:{qty}, supply price:{supply_price}...")
                    if response.status_code == 429:
                        gui.setStatus("Rate Limited while adding consignment product. Will continue after 5 minutes...")
                        print("rate limited at addConsignmentProductsReceived")
                        time.sleep(301)
                        response = api.addConsignmentProductReceived(consignmentId, pid, qty, supply_price)

    return negativeProds '''

def getPidToInventory(inventories):
    pidtoinv = {}

    for inv in inventories:
        prodId = inv['product_id']

        invlist = pidtoinv.get(prodId, None)
        # invlist = pidtoinv.get(prodId, []) #this should be the most efficient but not sure if this is not working

        if invlist is None:
            invlist = []

        invlist.append(inv)

        pidtoinv[prodId] = invlist

    return pidtoinv



def getInventoryWithPid(prodtoinventory):
    inventories = []

    for pid in prodtoinventory:
        invs = prodtoinventory[pid]['inventory']
        cost = prodtoinventory[pid]['cost']

        for i in invs:
            i['product_id'] = pid
            i['cost'] = cost
            inventories.append(i)

    return inventories

def getProdIdToOutletInventory(prodIdToInventory):

    pidtooutletinventory = {}

    for pid in prodIdToInventory:
        #oinventory = prodIdToInventory[pid]
        oinventory = prodIdToInventory.get(pid, None)

        #product doesn't exist
        if oinventory is None:
            continue

        for oi in oinventory:
            curroutid = oi['outlet_id']

            pidtooutletinventory[pid][curroutid] = oi


def getOutletIdToConsignment(consignments):

    idtoobj = {}

    for c in consignments:
        outletid = c['outlet_id']

        idtoobj[outletid] = c

    return idtoobj


def createStockOrders(api, outlets):

    stockOrders = []

    i = 0

    while i < len(outlets):
        o = outlets[i]

        cresponse = api.createStockOrder(outletid=o['id'], name=f"Fix Avg Cost - {o['name']}")
        status_code = cresponse.status_code

        if status_code == 429:
            print('ratelimited at createStockOrder')
            gui.setStatus("ratelimited at create stock order")
            time.sleep(300)
            continue

        if status_code == 200:
            rjson = cresponse.json()
            stockOrders.append(rjson)

        i += 1

    return stockOrders
    '''
    for o in outlets:
        cresponse = api.createStockOrder(o['id'], f"Fix Avg Cost - {o['name']}")

        if cresponse == 200:

        elif cresponse ==- 429:
            time.sleep(300)
            api.createStockOrder(o['id'], f"Fix Avg Cost - {o['name']}")
    '''

def filterProdIdInventories(ids, pidtoinv):
    idtoinv = {}

    for id in ids:
        pinv = pidtoinv[id]
        curridinv = idtoinv.get(id, None)

        #vals must be lists for multioutlet
        if curridinv is not None:
            curridinv.append(pinv)
            continue

        idtoinv[id] = [pinv]

    return idtoinv

def zeroOutInv(inventories, api):

    for inv in inventories:
        pid = inv['product_id']
        zeroinv = [{
            'outlet_id' : inv['outlet_id'],
            'count' : 0
        }]

        minpayload = {
            'id' : pid,
            'inventory' : zeroinv
        }
        response = api.updateProductInventory(**minpayload)

        if response.status_code == 429:
            print('ratelimited at zeroOutInventory')
            gui.setStatus("Rate limited at zeroOutInv")
            time.sleep(301)
            response = api.updateProductInventory(**minpayload)


#old way when using prod0.9 endpoint working on o(n) after using
#inventory endpoint to retrieve
def zeroOutInventory(idToInv, api):

    for id in idToInv:
        outletInventories = idToInv[id]['inventory']
        #print(outletInventories)
        minOutletsPayload = []
        for outletInv in outletInventories:
            #print(outletInv)
            minOutletsPayload.append(
                {
                    "outlet_id" : outletInv['outlet_id'],
                    "count" : 0
                }
            )

        response = api.updateProductInventory(id, minOutletsPayload)

        if response.status_code == 429:
            print('ratelimited at zeroOutInventory')
            gui.setStatus("Rate limited at zeroOutInventory")
            time.sleep(301)
            response = api.updateProductInventory(id, minOutletsPayload)

        #print(response.json())

def getProdIdToInventory(ids, idToObj):

    prodidtoinventory = {}

    #print(idToObj)

    for id in ids:
        obj = idToObj.get(id, None)

        #pid doens't exist
        if obj is None:
            gui.setStatus(f'{id} does not exist in store...')
            continue

        inventories = obj.get('inventory', None)

        if inventories is None:
            gui.setStatus(f'{id} has no inventory...')
            continue

        cost = obj['supply_price']

        prodidtoinventory[id] = {
            'inventory' : inventories,
            'cost' : cost
        }
        '''
        prodidtoinventory[id]['inventory'] = idToObj[id]['inventory']
        prodidtoinventory[id]['cost'] = idToObj[id]['supply_price']'''

    return prodidtoinventory

def getProdIdtoObj(fullProdList):

    prodIdToObj = {}

    for p in fullProdList:
        prodIdToObj[p['id']] = p

    return prodIdToObj

def getCsvProdsToFix():
    filenames = gui.csvList

    prodstofix = []
    for file in filenames:
        filepath = gui.getFilePath(file)

        if (filepath):
            prodstofix.extend(CsvUtil.getColumn(filepath, "id"))

    return prodstofix

def addActionEvents(user, app, date, numfixed):

    details = f"Number of mismatched products found: {numfixed}"

    toolusage.writeRow(**{
        "user" : user,
        "appfunction" : app,
        "completedon" : date,
        "prefix" : gui.getPrefix(),
        "ticketnum" : gui.getTicketNum(),
        "details" : details
    })

def setGlobalGui(thatgui):
    global gui

    gui = thatgui

def loadData(tool=None, git=None):

    global GITAPI
    global toolusage

    if tool is not None:
        toolusage = tool

    if git is not None:
        GITAPI = git
        return

    #for standalone for public with data to import
    #creds obviously not commited to repo
    try:
        with open('data.json') as f:
            data = json.load(f)
    except Exception:
        return




    ##print(f"{data['owner']}: {data['repo']} : {data['ghtoken']}")

    GITAPI = GitHubApi(owner=data['owner'], repo=data['repo'], token=data['ghtoken'])



    toolusage = ToolUsageSheets(credsfile=data['credjson'], \
                                sheetId=data['sheetId'], \
                                sheetName=USER)




if __name__ == "__main__":
    gui = VendFixAvgCostGUI(maincallback=startProcess)
    loadData()
    gui.main()
