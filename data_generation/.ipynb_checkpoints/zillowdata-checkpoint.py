import requests
import pandas as pd
import datetime
import time
import os
import glob
import pickle
import json


def ingestRentalData(name):
    date = datetime.datetime.now().date()
    start = time.time()

    with open('cities/' + str(name).lower(), 'rb') as f:
        city = pickle.load(f)

    z_data = pixLoad(city.getAreaZ())

    total_raw = 0
    total_final = 0
    address = []
    zips = []
    sqft = []
    baths = []
    beds = []
    lat = []
    long = []
    rent = []

    total_raw = len(z_data)
    for prop in (z_data):
        try:
            details = prop['hdpData']['homeInfo']
            taddress = str(details['streetAddress']) + ', ' + str(details['city']) + ', ' + str(details['state']) + ' ' + str(details['zipcode'])
            tzipcode = details['zipcode']
            tsqft = details['livingArea']
            tbaths = details['bathrooms']
            tbeds = details['bedrooms']
            tlat = details['latitude']
            tlong = details['longitude']
            tprice = details['price']

            address.append(taddress)
            zips.append(tzipcode)
            sqft.append(tsqft)
            baths.append(tbaths)
            beds.append(tbeds)
            lat.append(tlat)
            long.append(tlong)
            rent.append(tprice)
        except KeyError:
            continue

    total_final=len(address)
    df = pd.DataFrame()
    df['address'] = address
    df['zip'] = zips
    df['sqft'] = sqft
    df['baths'] = baths
    df['beds'] = beds
    df['lat'] = lat
    df['long'] = long
    df['rent'] = rent
    df.to_csv('zillow_data/' + name + '_' + str(date) + '.csv',index=False)

    run_time = time.time() - start

    f = open("metadata_zillow/metadata_" + str(name) + '_' + str(date), "w+")
    f.write('Total raw records: ' + str(total_raw) + '\n')
    f.write('Total processed records: ' + str(total_final) + '\n')
    f.write('Run time: ' + str(run_time) + '\n')


def ingestRawData(area):
    # area expected to be in format (west, east, south, north)
    print(area)
    params = (
        ('searchQueryState', '{"pagination":{},"mapBounds":{"west":' + str(area[0]) + ',"east":' + str(area[1]) + ',"south":' + str(area[2]) + ',"north":' + str(area[3]) + '},"isMapVisible":true,"mapZoom":12,"filterState":{"sortSelection":{"value":"days"},"isPreMarketForeclosure":{"value":false},"isPreMarketPreForeclosure":{"value":false},"isMakeMeMove":{"value":false},"isForSaleByAgent":{"value":false},"isAuction":{"value":false},"isForSaleByOwner":{"value":false},"isNewConstruction":{"value":false},"isForSaleForeclosure":{"value":false},"isComingSoon":{"value":false},"isForRent":{"value":true}},"isListVisible":true}'),
    )
    cookies = {
        '$abtest': '3|DJSQTLDcJiuB0qamMg',
        'search': '6|1564952188646%7Crect%3D43.388264780507974%252C-88.56601083744727%252C42.7935678134028%252C-90.11233652104102%26disp%3Dmap%26mdm%3Dauto%26p%3D1%26sort%3Ddays%26z%3D0%26fs%3D0%26fr%3D1%26mmm%3D0%26rs%3D0%26ah%3D0%26singlestory%3D0%26abo%3D0%26garage%3D0%26pool%3D0%26ac%3D0%26waterfront%3D0%26finished%3D0%26unfinished%3D0%26cityview%3D0%26mountainview%3D0%26parkview%3D0%26waterview%3D0%26hoadata%3D1%09%01%0981422%09%09%092%090%09US_%09',
        'zguid': '23|%247d1144f9-7c8e-4e27-b3ad-9836378dfa1c',
        'G_ENABLED_IDPS': 'google',
        '__gads': 'ID=a7fedfe8e08de9a8:T=1525434786:S=ALNI_MZsaf2tgyTZuE8tVt_FfADHrJ-C_Q',
        'ajs_user_id': '%22X1-ZU12oshfzsq2io9_5886z%22',
        'ajs_group_id': 'null',
        'ajs_anonymous_id': '%227d1144f9-7c8e-4e27-b3ad-9836378dfa1c%22',
        '_ga': 'GA1.2.1834088727.1540425398',
        '_mkto_trk': 'id:324-WZA-498&token:_mch-zillow.com-1543633758577-74649',
        'pxvid': '2afecbb0-f62e-11e8-b471-1b4eff18e8c1',
        '_pxvid': '2afecbb0-f62e-11e8-b471-1b4eff18e8c1',
        'optimizelyEndUserId': 'oeu1544487333690r0.5729256648330646',
        'ki_t': '1549722251082%3B1562358894899%3B1562360148715%3B10%3B21',
        'ki_r': '',
        'ki_s': '172156%3A0.0.0.0.2%3B198560%3A0.0.0.0.2%3B198561%3A0.0.0.0.2',
        'loginmemento': '1|6e885e2ca853efb9ff95e1bdbfae31b8cddb69f0112d20c12d49439641afe0b8',
        'userid': 'X|3|688e22eaafe11629%7C5%7CHMcR61sYPKjsKuiWyI_u5gmWppjLJGfU',
        'zjs_anonymous_id': '%227d1144f9-7c8e-4e27-b3ad-9836378dfa1c%22',
        'zjs_user_id': '%22X1-ZU12oshfzsq2io9_5886z%22',
        'ctm': '{\'pgv\':1723224511418464|\'vst\':3862653820528851|\'vstr\':8879895437522327|\'intr\':1558806529088|\'v\':1}',
        '__CT_Data': 'gpv=1&ckp=tld&dm=zillow.com&apv_82_www33=1&cpv_82_www33=1&rpv_82_www33=1',
        'WRUIDAWS': '2273036716490844',
        'AWSALB': 'aMPssDbN+qe2VETbuMCVogfXu9xNAZRC/zhrlmGzuYF7tlIShHEKOb0LAO5WeAapaU/390rZOEFru6PstBltvngIcflI6L6ykEhMGE41pG7Pott23rm+1Sbs/WsW',
        'zgsession': '1|1f5f1b73-2d31-4564-940d-a197d60f4673',
        'JSESSIONID': '779B6ABD738E6AC0CEECB035F5C80467',
        'ZILLOW_SID': '1|AAAAAVVbFRIBVVsVEvj%2B3skKywGJunfhlXcfm57SGfTmnhOdLS45QwKzRHwDkN2SLzulHTqDBd1mXdhFvqf6DQ8skrIV',
        'DoubleClickSession': 'true',
        '_csrf': 'iLE9LrdsnfvRli9unZVZQedz',
        'rental_csrftoken': '6hzJUzyE-s6tedIjaj167IcmKin0Wa8lzHoI',
        'swVersion': '-1',
        '__stripe_mid': '39b99158-f686-4771-bc25-d0b8717ae138',
        'FSsampler': '344853124',
        'ZG_SW_REGISTERED': 'true',
        'visitor_id701843': '22549385',
        'visitor_id701843-hash': '27fe56d0240fdc85cb704fe88f89b473be502a2969697ea9f32fe62d12b90acb808f44605df684114dd0aea1730f4f2118ccdedd',
        '_gid': 'GA1.2.1198746317.1562358846',
        '_gcl_au': '1.1.933772612.1562358847',
        'KruxPixel': 'true',
        'KruxAddition': 'true',
        '_px3': '1acd714127554e2da6b53330ce8b1182fc3eb1f9fb038e417f83ed19516e1da7:MkL8Dwo6xGgjjGuBgeAf22XW/qP7xyExtZguIdY7DcyWZNYjfBJNg6jy/P2PKUuMYpknduIPQWxwdmndHP6uyQ==:1000:6WLaAj493nlUcAV6vidnDNLeI2r0hawnqtcKqqibLjCUdDu8baTqM9KJKaTzF/8RQDniDwOu/h5WcWtjdHilDwzey9xadOPHasHm6S94iWBHsM2nv8arfNG4kZyJbqqu+TmwZs1Wv5fwh0T2ezLF6rHuKjVrCiP1bMTVOdgmDek=',
        '_gat': '1',
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:67.0) Gecko/20100101 Firefox/67.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.zillow.com/homes/for_rent/?searchQueryState={%22pagination%22:{},%22mapBounds%22:{%22west%22:-90.11233652104102,%22east%22:-88.56601083744727,%22south%22:42.7935678134028,%22north%22:43.388264780507974},%22isMapVisible%22:true,%22filterState%22:{%22sortSelection%22:{%22value%22:%22days%22},%22isForSaleByAgent%22:{%22value%22:false},%22isForSaleByOwner%22:{%22value%22:false},%22isNewConstruction%22:{%22value%22:false},%22isForSaleForeclosure%22:{%22value%22:false},%22isComingSoon%22:{%22value%22:false},%22isAuction%22:{%22value%22:false},%22isPreMarketForeclosure%22:{%22value%22:false},%22isPreMarketPreForeclosure%22:{%22value%22:false},%22isMakeMeMove%22:{%22value%22:false},%22isForRent%22:{%22value%22:true}},%22isListVisible%22:true}',
        'Connection': 'keep-alive',
    }

    response = requests.get('https://www.zillow.com/search/GetSearchPageState.htm', headers=headers, params=params, cookies=cookies)
    try:
        data = response.json()
        return data
    except json.decoder.JSONDecodeError:
        return []


def getZData(city, zipcodes=[], date_override='', filename_override=''):
    date = str(datetime.datetime.now().date())
    filename = ''

    if (filename_override != ''):
        # load based on filename
        filename = filename_override
    else:
        # load based on date
        if (date_override != ''):
            date = date_override
        # find the most recent file for the given city and date
        filename = max(glob.iglob("zillow_data/" + str(city) + "*.csv"), key=os.path.getmtime)
    # load the file in
    if (zipcodes==[]):
        df_raw = pd.read_csv(filename)
        df_raw.reset_index(inplace=True)
        return df_raw

    print(filename)
    df_raw = pd.read_csv(filename)

    df_f = df_raw[df_raw['zip'].astype(str)==str(zipcodes[0])]
    # for each zipcode
    for zipcode in zipcodes[1:]:
        df_temp = df_raw[df_raw['zip'].astype(str)==str(zipcode)]
        df_f = pd.concat([df_f, df_temp],ignore_index=True)
    df_f.reset_index(inplace=True)

    return df_f


def updateZips(city):
    # get most recent HS raw data
    date = str(datetime.datetime.now().date())
    filename = max(glob.iglob("zillow_data/" + str(city) + "_" + str(date) + "*.csv"), key=os.path.getmtime)
    df_raw = pd.read_csv(filename)

    raw_zips = set(df_raw['zip'])

    with open('cities/' + city.lower(), 'rb') as f:
        city_data = pickle.load(f)
    city_zips = set(city_data.getZips())

    city_zips_new = city_zips.union(raw_zips)
    city_data.setZips(list(city_zips_new))
    with open('cities/' + city.lower(), 'wb') as f:
        pickle.dump(city_data,f)


def pixLoad(area):
    data = ingestRawData(area)
    if (data == []):
        return data
    if (len(data['searchResults']['mapResults']) < 500):
        print(len(data['searchResults']['mapResults']))
        return data['searchResults']['mapResults']
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
