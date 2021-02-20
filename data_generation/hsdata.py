# %%
import re
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import pandas as pd
import numpy as np
import time
import datetime
import json
import os
import glob
import pickle

# %%
session = requests.Session()
retry = Retry(connect=50, backoff_factor=1.0)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

# constant parameters needed to make the CURL call
cookies = {
    'User': 'ID=363963251&Hash=c0b34aefa4bd99fbb739db18210795640e907c23',
    'ASP.NET_SessionId': 'utgd3ixcmpklcqv1hvihrzzh',
    'SERVERID': 'web8',
}

headers = {
    'Pragma': 'no-cache',
    'Origin': 'https://www.homesnap.com',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/70.0.3538.110 Chrome/70.0.3538.110 Safari/537.36',
    'Content-Type': 'application/json; charset=UTF-8',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Cache-Control': 'no-cache',
    'X-Requested-With': 'XMLHttpRequest',
    'Connection': 'keep-alive',
    'Referer': 'https://www.homesnap.com/homes/for_sale/Wisconsin/p_21,50/c_43.07799,-89.396323/z_13',
    'DNT': '1',
}


# %%
def ingestData(name, metadata=False):
    global headers
    global cookies
    start_time = time.time()

    date = datetime.datetime.now().date()
    if (metadata):
        f = open("metadata_listing/metadata_" + str(name) + '_' + str(date), "w+")

    with open('cities/' + str(name).lower(), 'rb') as fc:
        city = pickle.load(fc)

    area = city.getAreaH()
    data = pixLoad(area)

    listings = []
    urls_f = []
    lats = []
    longs = []
    unit_c = []
    price = []
    beds = []
    baths = []
    sqft = []
    street_address = []
    city_state = []
    address_f = []
    zips = []
    yearBuilt = []
    propertyType = []
    propertyType2 = []
    cont = []
    list_date = []
    original_price = []

    for listing in data:
        listings.append(listing['ListingID'])
        try:
            urls_f.append('https://www.homesnap.com' + listing['Url'])
        except TypeError:
            urls_f.append(None)
        lats.append(listing['Latitude'])
        longs.append(listing['Longitude'])
        unit_c.append(listing['UnitCount'])
        price.append(listing['Price'])
        beds.append(listing['Beds'])
        street_address.append(listing['FullStreetAddress'])
        city_state.append(listing['Label'])
        address_f.append(street_address[-1] + ', ' + city_state[-1])
        zips.append(listing['Zip'])
        if (listing['BathsFull'] is not None):
            if (listing['BathsHalf'] is not None):
                baths.append(float(listing['BathsFull']) + .5 * float(listing['BathsHalf']))
            else:
                baths.append(float(listing['BathsFull']))
        else:
            baths.append(0)
        sqft.append(listing['SqFt'])
        yearBuilt.append(listing['YearBuilt'])
        propertyType.append(listing['SPropertyType'])
        propertyType2.append(listing['SPropertyType2'])

        ld = listing['Listing']['ListDate']
        ld = re.search('(\d+)',ld)[0][0:-3]
        ts = int(ld)
        list_date.append(datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d'))

        original_price.append(listing['Listing']['OriginalPrice'])

        if (listing['Listing']['ContractDate'] is None):
            cont.append('No')
        else:
            cont.append('Yes')

    if (metadata):
        f.write('Number of listings: ' + str(len(listings)) + '\n')
        time_initial_listings = time.time()
        f.write('Time for high level listing information: ' + str(time_initial_listings - start_time) + '\n')

    # get rents
    rents = []
    for index, listid in enumerate(listings):
        if (propertyType2[index]!=16):
            rents.append(0)
            continue

        params1 = '{"listingID":' + str(listid) + ',"parts":506}'
        try:
            response = requests.post('https://www.homesnap.com/service/Listings/GetDetails',headers=headers,cookies=cookies,data=params1)
        except requests.exceptions.ConnectionError:
            time.sleep(60)
            response = requests.post('https://www.homesnap.com/service/Listings/GetDetails',headers=headers,cookies=cookies,data=params1)

        try:
            details = response.json()['d']
        except json.decoder.JSONDecodeError:
            details = None

        if (details is None):
            rents.append(0)
        else:
            tot = city.parseRent(details)
            rents.append(tot)

    if (metadata):
        time_details = time.time()
        f.write('Time for detailed listing information: ' + str(time_details - time_initial_listings) + '\n')

    df = pd.DataFrame()

    df['contingent'] = cont
    df['units'] = unit_c
    df['beds'] = beds
    df['baths'] = baths
    df['sqft'] = sqft
    df['rent'] = rents
    df['list_price'] = price
    df['address'] = address_f
    df['zip'] = zips
    df['urls'] = urls_f
    df['listings'] = listings
    df['lats'] = lats
    df['longs'] = longs
    df['year_built'] = yearBuilt
    df['beds'] = beds
    df['street_address'] = street_address
    df['city_state'] = city_state
    df['list_date'] = list_date
    df['original_price'] = original_price
    df['propertyType'] = propertyType
    df['propertyType2'] = propertyType2

    if (metadata):
        f.write('Non-zero rents: ' + str(len(df[df['rent']>0])) + '\n')
        f.write('Multi-unit properties: ' + str(len(df[df['units']>1])) + '\n')
        f.write('Number contingent: ' + str(len(df[df['contingent']=='Yes'])) + '\n')
        f.write('Number of properties final: ' + str(len(df)))
        f.close()

    df.to_csv('listing_data/' + name + '_' + str(date) + '.csv',index=False)


# %%
def findRentFields(listings,urls_f):
    pot_rent = set()
    urls_rents = []
    time_start = time.time()
    for index, listid in enumerate(listings):
        params1 = '{"listingID":' + str(listid) + ',"parts":506}'
        response = requests.post('https://www.homesnap.com/service/Listings/GetDetails',headers=headers,cookies=cookies,data=params1)
        details = response.json()['d']

        if (details is None):
            continue
        else:
            for fact in details['Details']:
                for field in fact['Fields']:
                    if (re.search('income',field['Name'],re.IGNORECASE) or (re.search('rent',field['Name'],re.IGNORECASE))):
                        print(fact['Name'])
                        print(field['Name'])
                        print(urls_f[index])
                        size_b = len(pot_rent)

                        pot_rent.add((fact['Name'],field['Name']))

                        size_a = len(pot_rent)
                        if (size_a > size_b):
                            urls_rents.append(urls_f[index])
    print(time.time() - time_start)
    return (pot_rent,urls_rents)


# %%
def getHsData(city, zipcodes=[], date_override='', filename_override=''):
    date = str(datetime.date.today())
    if (zipcodes==[]):
        filename = max(glob.iglob("listing_data/" + str(city) + "*.csv"), key=os.path.getmtime)
        df_raw = pd.read_csv(filename)
        df_raw.reset_index(inplace=True)
        return df_raw

    filename = ''
    if (filename_override != ''):
        # load based on filename
        filename = filename_override
    else:
        # load based on date
        if (date_override != ''):
            date = date_override
        # find the most recent file for the given city and date
        filename = max(glob.iglob("listing_data/" + str(city) + "_" + "*.csv"), key=os.path.getmtime)
    # load the file in
    print(filename)
    df_raw = pd.read_csv(filename)
    df_f = df_raw[df_raw['zip']==zipcodes[0]]
    # for each zipcode
    for zipcode in zipcodes[1:]:
        df_temp = df_raw[df_raw['zip']==zipcode]
        df_f = pd.concat([df_f, df_temp],ignore_index=True)
    df_f.reset_index(inplace=True)


# %%
def updateZips(city):
    # get most recent HS raw data
    date = str(datetime.datetime.now().date())
    filename = max(glob.iglob("listing_data/" + str(city) + "_" + str(date) + "*.csv"), key=os.path.getmtime)
    df_raw = pd.read_csv(filename)

    raw_zips = set(df_raw['zip'])

    with open('cities/' + city.lower(), 'rb') as f:
        city_data = pickle.load(f)
    city_zips = set(city_data.getZips())

    city_zips_new = city_zips.union(raw_zips)
    city_data.setZips(list(city_zips_new))
    with open('cities/' + city.lower(), 'wb') as f:
        pickle.dump(city_data,f)


# %%
def pixLoad(area):
    data = ingestRawData(area)
    if (len(data['d']['Listings']) < 10000):
        print(len(data['d']['Listings']))
        return data['d']['Listings']
    width = area[1] - area[0]
    print(width)
    height = area[3] - area[2]
    print(height)
    if (width > height):
        # split horizontally.
        # Left
        dataLeft = pixLoad((area[0], area[0] + width/2, area[2], area[3]))
        # right
        dataRight = pixLoad((area[0] + width/2, area[1], area[2], area[3]))
        return (dataLeft + dataRight)
    else:
        # split vertically
        # top
        dataTop = pixLoad((area[0], area[1], area[2] + height/2, area[3]))
        # bottom
        dataBottom = pixLoad((area[0], area[1], area[2], area[2] + height/2))
        return (dataTop + dataBottom)


# %%
def ingestRawData(area):
    params = '{"latitudeMin":' + str(area[0]) + ',"latitudeMax":' + str(area[1]) + ',"longitudeMin":'+ str(area[2]) + ',"longitudeMax":' + str(area[3]) + ',"sPropertyType2":511,"sListingStatus":1,"specialFeatures":0,"bathsMin":0,"bathsMax":50,"bedsMin":0,"bedsMax":100,"priceMin":0,"priceMax":100000000,"dateRange":0,"sortOrder":1,"listingCount":10000000,"clusterCount":27}'
    # gets the overall property data
    response = requests.post('https://www.homesnap.com/service/Listings/GetByBoundingBox', headers=headers, cookies=cookies, data=params)
    # decode the information and get it in an intelligible format
    response.iter_content(chunk_size=10240, decode_unicode=False)
    data = response.json()
    return data
