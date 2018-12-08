import requests

class VendApi:
    """
        Basic VendApi Class that has the functionality to call and return
        the objects of the corresponding types (customers, sales).
        Will need to add on to the class for others if needed.

        Author: Sung Min Yoon
    """

    __BASE_URL = "https://{0}.vendhq.com/"
    __ENDPOINTS = {
        "cust" : "api/2.0/customers",
        "search" : "api/2.0/search",
        "sales" : "api/2.0/sales"
    }

    __domain = ''
    __headers = {"Authorization" : "", "User-Agent" : "Python 3.7/Vend-Support-Tool"}
    __prefix = ''

    def __init__(self, prefix, token):
        """
            Constructor to set the provided prefix and token of the store to
            work with.
        """
        self.__domain = self.__BASE_URL.format(prefix)
        self.__headers["Authorization"] = "Bearer " + token
        self.__prefix = prefix

    def deleteCustomer(self, id):
        """
            Deletes a customer based on the provided ID. Returns the status code
            of the response.

            204: Successfully deleted
            500: Could not delete because of customer attached to open sale(s)
            404: No such customer exists to delete.
        """
        return requests.request("DELETE", '{0}{1}/{2}'.format(self.__domain, self.__ENDPOINTS['cust'], id), headers=self.__headers).status_code

    def getCustomers(self):
        """
            Returns array of customer objects of this store.
        """
        #return self.__getRequest__(self.__domain + self.__ENDPOINTS['cust'] + "?deleted=" + str(False))
        return self.__getSearch__(url=self.__domain + self.__ENDPOINTS['search'], type='customers')

    def getOnAccountSales(self):
        """
            Returns array of on-account sales for this store.
        """
        return self.__getSearch__(self.__domain + self.__ENDPOINTS['search'] + '?type=sales&status=onaccount')

    def getLaybySales(self):
        """
            Returns array of layby sales for this store.
        """
        return self.__getSearch__(self.__domain + self.__ENDPOINTS['search'] + '?type=sales&status=layby')

    def __getSearch__(self, url, type='', deleted='false', offset='', pageSize='10000'):
        """
            Base method for search API calls. Returns the 'data' array of the
            corresponding objects. Returns None if the request is unsuccessful.
            Currently, the regular customers endpoint doesn't work properly
            with deleted flag; this will have to do at the moment.
        """
        search = "{0}?type={1}&deleted={2}&page_size={3}&offset={4}"
        endpoint = search.format(url, type, deleted, pageSize, offset)
        response = requests.request("GET", endpoint, headers = self.__headers)

        if response.status_code != 200:
            return None

        data = []
        tempJson = response.json()['data']
        offset = '10000'

        while len(tempJson) > 0:
            data.extend(tempJson)
            endpoint = search.format(url, type, deleted, pageSize, offset)
            tempJson = requests.request("GET", endpoint, headers = self.__headers).json()['data']

        return data

    def getOpenSales(self):
        """
            Returns an array of all open sales of this store.  Layby and
            on-account sales.
        """

        tempOpenSales = []
        tempOpenSales.extend(self.getOnAccountSales())
        tempOpenSales.extend(self.getLaybySales())

        return tempOpenSales

    def getPrefix(self):
        """
            Returns this store's domain prefix.
        """
        return self.__prefix

    def __getRequest__(self, url):
        """
            Base method for regular API calls. Returns the 'data' array of the
            corresponding objects. Returns None if the request is unsuccessful.
            Will get all results based on the pagination, max version.
        """
        response = requests.request("GET", url, headers = self.__headers)

        if response.status_code != 200:
            return None

        # gotta check if the url already has params for search
        # no ternary in python?
        if "?" in url:
            cursorParam = "&after={0}"
        else:
            cursorParam = "?after={0}"

        tempDataList = []
        tempJson = response.json()
        version = tempJson['version']['min']

        while version is not None:
            tempDataList.extend(tempJson['data'])

            if tempJson['version']['max'] is None:
                break;

            version = tempJson['version']['max']

            tempJson = requests.request("GET", url + cursorParam.format(version), headers = self.__headers).json()

        return tempDataList
