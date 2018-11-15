#-------------------------------------------------------------------------------
# CACHING.PY
# All caching though API and Scraping is handled here.
#-------------------------------------------------------------------------------

import requests
import time
import datetime as dt
import json
from bs4 import BeautifulSoup

class CacheFile():
    def __init__(self, filename, print_info=False):
        self.filename = filename
        self.API_cache = {}
        self.print_info = print_info
        self.last_request = dt.datetime.now()
        # Try to open the cache file if you can find it and load the json data into API_cache
        try:
            with open(self.filename, 'r') as f:
                self.API_cache = json.loads(f.read())
        except Exception as e:
            print("No cache file named {} exists or I can't read it properly. Creating one now...".format(self.filename))
            f = open(self.filename, 'w')
            f.close()

    # Makes a request for a given url and saves it to the cache file
    # params: unique_ID: a unique identifier for this request. Usually the url and any soup-straining done
    #         url: the url to request
    #         header: if a header is needed. default is None
    #         strainer: a SoupStrainer object that restricts the data needed to be saved to the cache. default is None
    #         print_info: If set true, will print details about the request to the console.
    # returns: nothing
    def Make_Request(self, unique_ID, url, header=None, strainer=None):
        start = time.clock()
        html_text = requests.get(url, headers=header).text
        soup = BeautifulSoup(html_text, 'html.parser')
        strained_soup = soup.find_all(strainer)
        self.API_cache[unique_ID] = {"accessed":str(dt.datetime.now()), "html":str(strained_soup)}
        end = time.clock()
        if self.print_info: print("Request completed in " + str(end-start)[:6] + "ms")

        start = time.clock()
        with open(self.filename, 'w') as f:
            f.write(json.dumps(self.API_cache)) # write the contents of the cache dictionary to the cache
        end = time.clock()
        if self.print_info: print("Save to Cache file completed in " + str(end-start)[:6] + "ms")

    # Checks the cache file to see if this url has already been stored in the cache
    # params: url: a string for the url,
    #         header: any required headers.
    #         max_age: a datetime.timedelta object that indicates the maximum age a cached object should have. Over this, a new request is made
    #         strainer: A SoupStrainer object can be used to filter the response so we're not cahching the entire page
    #         print_info=true gives debugging info and timings.
    # returns: a dictionary of json, either pulled from the API or loaded from the cache
    def CheckCache_Soup(self, url, header=None, max_age=None, strainer=None):
        unique_ID = url # start creating the unique_ID with the URL
        if strainer is not None:
            unique_ID += "_strain(" + str(strainer) + ")"

        if self.print_info: print("Checking cache for " + unique_ID[:40] + "...")
        # check to see if this unique ID is stored in the cache, and if not, make a request and add it
        if unique_ID in self.API_cache:
            if self.print_info: print("Repeated request - retrieving from cache file.")

            # if we do have a max age and this ID is in the cache, check to see if we're past it, in which case set out_of_date to true so we pull a new cache entry
            if max_age is not None:
                if self.print_info: print("last accessed " + self.API_cache[unique_ID]['accessed'])
                dt_last_access = dt.datetime.strptime(self.API_cache[unique_ID]['accessed'], "%Y-%m-%d %H:%M:%S.%f") # 2018-02-27 20:28:56.492553
                if (dt.datetime.now() - dt_last_access) > max_age:
                    if self.print_info: print("cache out of date - refreshing...")
                    self.Make_Request(unique_ID, url, header, strainer)
        else:
            if self.print_info: print("New request - adding to cache file.")
            self.Make_Request(unique_ID, url, header, strainer)

        return BeautifulSoup(self.API_cache[unique_ID]['html'], 'html.parser')

    # Checks the cache file for a combination of url and keys to see if this API call exists in the cache already.
    # params: a string for the url
    #         a dictionary of paramaters for the API
    #         (optional) a timedelta for the age at which data would be considered stale
    #         (optional) a list of specific keys to store in the cache, which cuts down on access time for large cache files
    # returns: a dictionary of json, either pulled from the API or loaded from the cache
    def CheckCache_API(self, url, params, max_age=None, keys=None, rate_limit=False, force_update=False):
        param_keys = sorted(params.keys()) # sort the paramaters so we know they'll be in the same order even if they aren't in order in the dictionary attribute
        unique_ID = url # start creating the unique_ID with the URL
        for k in param_keys:
            if not("api" in k and "key" in k): # skip anything with the words "api" and "key"
                unique_ID += "_" + k + "_" + str(params[k]).lower()
        if keys is not None:
            unique_ID += '_' + '_'.join(keys)

        # check to see if this unique ID is stored in the cache, and if not, make a request and add it
        if unique_ID in self.API_cache:
            if force_update:
                if self.print_info: print("Forced update")
            elif max_age is not None:
                age = time.time() - self.API_cache[unique_ID]["accessed"]
                if  dt.timedelta(seconds=age) > max_age:
                    if self.print_info: print("Request is more than {} old. Refreshing data....".format(max_age))
                else:
                    if self.print_info: print("Request is less than {} old. Loading from cache....".format(max_age))
                    return self.API_cache[unique_ID]["data"]
            else:
                if self.print_info: print("Repeated request - retrieving from cache file.")
                return self.API_cache[unique_ID]["data"]
        else:
            if self.print_info: print("New request - adding to cache file.")

        if rate_limit:
            time.sleep(.1)

        response = requests.get(url, params=params)
        if keys is None:
            to_save = json.loads(response.text)
        else:
            total_response_json = json.loads(response.text)
            to_save = {}
            for k in keys:
                to_save[k] = total_response_json[k]

        self.API_cache[unique_ID] = {}
        self.API_cache[unique_ID]["data"] = to_save
        self.API_cache[unique_ID]["accessed"] = time.time()

        with open(self.filename, 'w') as f:
            f.write(json.dumps(self.API_cache)) # write the contents of the cache dictionary to the cache
        return to_save
