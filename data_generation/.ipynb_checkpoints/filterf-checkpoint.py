import hsdata as hs
import pandas as pd
import datetime
import zillowdata as zd
import censushelper as ch
import geopy.distance
import numpy as np
import emailer
import pickle
import glob
import os
from scipy.spatial import distance

def stageData(city):
    # get the requested city. Contains data like zipcodes, lat, long areas etc.
    with open('cities/' + city.lower(), 'rb') as f:
        city_data = pickle.load(f)

    # get the listing data
    df_hs = hs.getHsData(city)
    
    # remove commercial and land listings
    df_hs = df_hs[(df_hs['propertyType2']!=128) & (df_hs['propertyType2']!=32)]

    # if units is blank, replace with the implied unit count based on the property type
    df_hs.loc[((df_hs['propertyType2'].isin([1,4,8,64])) & (df_hs['units'].isna())), 'units'] = 1
    addresses, lats, longs = list(df_hs['address']), list(df_hs['lats']), list(df_hs['longs'])
    df_hs = df_hs.reset_index()

    # enable for census data
    df = ch.get_census_df(df_hs)
    
    # listing df
    df['point'] = [(df['lats'].values[i], df['longs'].values[i]) for i in range(len(df))]

    # rental df
    df_z = zd.getZData(city)
    lats_s, longs_s = list(df_z['lat']), list(df_z['long'])
    df_z = df_z.reset_index()
    df_z = df_z[['address', 'zip', 'sqft', 'baths', 'beds', 'lat', 'long', 'rent']]
    df_z['rent_per_bed'] = df_z['rent']/df_z['beds']
    df_z['rent_per_sqft'] = df_z['rent']/df_z['sqft']
    df_z['point'] = [(df_z['lat'].values[i], df_z['long'].values[i]) for i in range(len(df_z))]

    if list(df_z['point'].values) != []:
        dist_matrix = distance.cdist(list(df['point'].values), list(df_z['point'].values), 'euclidean')

        # k nearest neighbors
        k = 6 

        rent_fs = []
        rent_fb = []
        for i in range(len(df)):
            nn_inds = np.argsort(dist_matrix[i])[:k]

            # sqft
            rent_fs_arr = df_z.iloc[nn_inds]['rent_per_sqft'].values
            rent_fs_arr = rent_fs_arr[np.isfinite(rent_fs_arr)]
            rent_fs_est = np.mean(rent_fs_arr)*df_hs.iloc[i]['sqft']
            rent_fs.append(rent_fs_est)

            # beds
            rent_fb_arr = df_z.iloc[nn_inds]['rent_per_bed'].values
            rent_fb_arr = rent_fb_arr[np.isfinite(rent_fb_arr)]
            rent_fb_est = np.mean(rent_fb_arr)*df_hs.iloc[i]['beds']
            rent_fb.append(rent_fb_est)

        df['rent_estimate_sqft'] = rent_fs
        df['rent_estimate_beds'] = rent_fb

    else:
        df['rent_estimate_sqft'] = [np.nan]*len(df_hs)
        df['rent_estimate_beds'] = [np.nan]*len(df_hs)

    # Investment metrics
    mortgage = []
    dp_p_close = []
    cf = []
    
    # Geographic specific
    pt_r = 0.024
    dp_r = 0.20
    i_rate = 0.05
    cc = 4000
    maint = 1000
    ins = 800

    for i in range(len(df)):
        mortgage.append(np.round((i_rate/(1-(1+(i_rate/12))**(-1*12*30)))*(df['list_price'].values[i]-dp_r*df['list_price'].values[i])))
        dp_p_close.append(np.round(dp_r*df['list_price'].values[i]+cc))
        cf.append(np.round(12*df['rent'].values[i]-mortgage[i]-(maint+ins+pt_r*df['list_price'].values[i])))

    df['mortgage'] = mortgage
    df['dp+close'] = dp_p_close
    df['1yr CF'] = cf
    df['price_to_rent_est_sqft'] = df['list_price'] / (df['rent_estimate_sqft'] * 12)
    df['price_to_rent_est_beds'] = df['list_price'] / (df['rent_estimate_beds'] * 12)
    df['price_to_rent'] = df['list_price'] / (df['rent'] * 12)

    # formatting/display changes
    df.loc[(df['rent']==0.0), 'rent'] = 'NA'

    columns = ['address', 'zip', 'units', 'list_price', 'rent', 'rent_estimate_beds','rent_estimate_sqft', 'beds', 'sqft', 'year_built', 'contingent', 'baths', 'list_date','original_price', 'mortgage', 'dp+close', '1yr CF', '1yr growth', '3yr growth', '5yr growth', 'unemploy %', 'family %', 'college %', 'poverty %', 'vacancy', 'med_age', 'price_to_rent','price_to_rent_est_sqft','price_to_rent_est_beds']
    df_f = pd.DataFrame()

    df_f['contingent'] = df['contingent']
    df_f['units'] = df['units']
    df_f['beds'] = df['beds']
    df_f['baths'] = df['baths']
    df_f['sqft'] = df['sqft']
    df_f['year_built'] = df['year_built']
    df_f['rent'] = df['rent']
    df_f['rent_estimate_sqft'] = df['rent_estimate_sqft']
    df_f['rent_estimate_beds'] = df['rent_estimate_beds']
    df_f['list_price'] = df['list_price']
    df_f['address'] = df['address']
    df_f['zip'] = df['zip']

    # enable for census data
    df_f['1yr growth'] = df['1yr growth']
    df_f['3yr growth'] = df['3yr growth']
    df_f['5yr growth'] = df['5yr growth']
    df_f['med_age'] = df['med_age']
    df_f['unemploy %'] = df['unemploy %']
    df_f['family %'] = df['family %']
    df_f['college %'] = df['college %']
    df_f['vacancy'] = df['vacancy']
    df_f['poverty %'] = df['poverty %']

    df_f['list_date'] = df['list_date']
    df_f['original_price'] = df['original_price']
    df_f['propertyType'] = df['propertyType2']
    df_f['lat'] = df['lats']
    df_f['lng'] = df['longs']
    df_f['mortgage'] = df['mortgage']
    df_f['dp+close'] = df['dp+close']
    df_f['1yr CF']= df['1yr CF']
    df_f['price_to_rent'] = df['price_to_rent']
    df_f['price_to_rent_est_sqft'] = df['price_to_rent_est_sqft']
    df_f['price_to_rent_est_beds'] = df['price_to_rent_est_beds']

    # rank by actual price to rent ratio
    df_f = df_f[df_f['contingent'] == 'No'].drop(columns='contingent')
    df_f = df_f.sort_values(by='price_to_rent',ascending=True)

    date = datetime.date.today()
    filename_staged = 'staged_data/' + city +'_filter_result_' + str(date) + '.pkl'
    df_f.to_pickle(filename_staged)

def combineFilters(location_names, name):
    curr_date = datetime.datetime.now().date()
    filters = []
    for location in location_names:
        filename = max(glob.iglob("./staged_data/" + str(location) + "*.pkl"), key=os.path.getmtime)
        df = pd.read_pickle(filename)
        df['county']=location
        filters.append(df)

    df_f = pd.DataFrame()

    for d in filters:
        df_f = df_f.append(d,ignore_index=True)

    df_f.sort_values('price_to_rent',inplace=True)
    df_f.to_pickle("staged_data/" + name + "_" + str(curr_date) + ".pkl")


def stageDataForDB(city):
    # get the requested city. Contains data like zipcodes, lat, long areas etc.
    with open('cities/' + city.lower(), 'rb') as f:
        city_data = pickle.load(f)

    # get the listing data
    df_hs = hs.getHsData(city_data.getZips(),city)
    
    # remove commercial and land listings
    df_hs = df_hs[(df_hs['propertyType2']!=128) & (df_hs['propertyType2']!=32)]

    # if units is blank, replace with the implied unit count based on the property type
    df_hs.loc[((df_hs['propertyType2'].isin([1,4,8,64])) & (df_hs['units'].isna())), 'units'] = 1
    addresses, lats, longs = list(df_hs['address']), list(df_hs['lats']), list(df_hs['longs'])
    df_hs = df_hs.reset_index()
    
    df_c = cd.get_census_df(addresses,lats,longs)
    df_c = df_c.reset_index()
    df = pd.concat([df_hs, df_c], axis=1)

    # listing df
    df_hs['point'] = [(df_hs['lats'].values[i], df_hs['longs'].values[i]) for i in range(len(df_hs))]

    # rental df
    df = df_hs
    df_z = zd.getZData(city)
    lats_s, longs_s = list(df_z['lat']), list(df_z['long'])
    df_z = df_z.reset_index()
    df_z = df_z[['address', 'zip', 'sqft', 'baths', 'beds', 'lat', 'long', 'rent']]
    df_z['rent_per_bed'] = df_z['rent']/df_z['beds']
    df_z['rent_per_sqft'] = df_z['rent']/df_z['sqft']
    df_z['point'] = [(df_z['lat'].values[i], df_z['long'].values[i]) for i in range(len(df_z))]

    if list(df_z['point'].values) != []:
        dist_matrix = distance.cdist(list(df_hs['point'].values), list(df_z['point'].values), 'euclidean')

        # k nearest neighbors
        k = 6 

        rent_fs = []
        rent_fb = []
        for i in range(len(df_hs)):
            nn_inds = np.argsort(dist_matrix[i])[:k]

            # sqft
            rent_fs_arr = df_z.iloc[nn_inds]['rent_per_sqft'].values
            rent_fs_arr = rent_fs_arr[np.isfinite(rent_fs_arr)]
            rent_fs_est = np.mean(rent_fs_arr)*df_hs.iloc[i]['sqft']
            rent_fs.append(rent_fs_est)

            # beds
            rent_fb_arr = df_z.iloc[nn_inds]['rent_per_bed'].values
            rent_fb_arr = rent_fb_arr[np.isfinite(rent_fb_arr)]
            rent_fb_est = np.mean(rent_fb_arr)*df_hs.iloc[i]['beds']
            rent_fb.append(rent_fb_est)

        df['rent_estimate_sqft'] = rent_fs
        df['rent_estimate_beds'] = rent_fb

    else:
        df['rent_estimate_sqft'] = [np.nan]*len(df_hs)
        df['rent_estimate_beds'] = [np.nan]*len(df_hs)

    # Investment metrics
    mortgage = []
    dp_p_close = []
    cf = []
    
    # Geographic specific
    pt_r = 0.024
    dp_r = 0.035
    i_rate = 0.05
    cc = 4000
    maint = 1000
    ins = 800

    for i in range(len(df)):
        mortgage.append(np.round((i_rate/(1-(1+(i_rate/12))**(-1*12*30)))*(df['list_price'].values[i]-dp_r*df['list_price'].values[i])))
        dp_p_close.append(np.round(dp_r*df['list_price'].values[i]+cc))
        cf.append(np.round(12*df['rent'].values[i]-mortgage[i]-(maint+ins+pt_r*df['list_price'].values[i])))

    df['mortgage'] = mortgage
    df['dp+close'] = dp_p_close
    df['1yr CF'] = cf
    df['price_to_rent_est_sqft'] = df['list_price'] / (df['rent_estimate_sqft'] * 12)
    df['price_to_rent_est_beds'] = df['list_price'] / (df['rent_estimate_beds'] * 12)
    df['price_to_rent'] = df['list_price'] / (df['rent'] * 12)

    # formatting/display changes
    df.loc[(df['rent']==0.0), 'rent'] = 'NA'

    columns = ['address', 'zip', 'units', 'list_price', 'rent', 'rent_estimate_beds','rent_estimate_sqft', 'beds', 'sqft', 'year_built', 'contingent', 'baths', 'mortgage', 'dp+close', '1yr CF', '1yr growth', '3yr growth', '5yr growth', 'unemploy %', 'family %', 'college %', 'poverty %', 'vacancy', 'med_age', 'price_to_rent','price_to_rent_est_sqft','price_to_rent_est_beds', 'lat', 'lng', 'propertyType']
    df_f = pd.DataFrame(columns=columns)

    df_f['contingent'] = df['contingent']
    df_f['units'] = df['units']
    df_f['beds'] = df['beds']
    df_f['baths'] = df['baths']
    df_f['sqft'] = df['sqft']
    df_f['year_built'] = df['year_built']
    df_f['rent'] = df['rent']
    df_f['rent_estimate_sqft'] = df['rent_estimate_sqft']
    df_f['rent_estimate_beds'] = df['rent_estimate_beds']
    df_f['list_price'] = df['list_price']
    df_f['address'] = df['address']
    df_f['zip'] = df['zip']

    df_f['1yr growth'] = df['1yr growth']
    df_f['3yr growth'] = df['3yr growth']
    df_f['5yr growth'] = df['5yr growth']
    df_f['med_age'] = df['med_age']
    df_f['unemploy %'] = df['unemploy %']
    df_f['family %'] = df['family %']
    df_f['college %'] = df['college %']
    df_f['vacancy'] = df['vacancy']
    df_f['poverty %'] = df['poverty %']

    df_f['mortgage']= df['mortgage']
    df_f['dp+close']= df['dp+close']
    df_f['1yr CF']= df['1yr CF']
    df_f['price_to_rent'] = df['price_to_rent']
    df_f['price_to_rent_est_sqft'] = df['price_to_rent_est_sqft']
    df_f['price_to_rent_est_beds'] = df['price_to_rent_est_beds']
    df_f['lat'] = df['lats']
    df_f['lng'] = df['longs']
    df_f['propertyType'] = df['propertyType2']

    # rank by actual price to rent ratio
    df_f = df_f[df_f['contingent'] == 'No'].drop(columns='contingent')
    df_f = df_f.sort_values(by='price_to_rent',ascending=True)

    date = datetime.date.today()
    filename_staged = 'staged_data_DB/' + city +'_filter_result_' + str(date) + '.pkl'
    df_f.to_pickle(filename_staged)


def generateReport(city,email,zipcodes=[],trial=False):
    filename = max(glob.iglob("staged_data/" + str(city) + "*.pkl"), key=os.path.getmtime)
    print(filename)

    df = pd.read_pickle(filename)

    if (zipcodes != []):
        df_f = df[df['zip']==zipcodes[0]]
        for zipcode in zipcodes[1:]:
            df_temp = df[df['zip']==zipcode]
            df_f = pd.concat([df_f,df_temp])
    else:
        df_f = df

    if (trial):
        df_f['rent_estimate_sqft'] = 'Not available in trial'
        df_f['rent_estimate_beds'] = 'Not available in trial'

        df_f['1yr growth'] = 'Not available in trial'
        df_f['3yr growth'] = 'Not available in trial'
        df_f['5yr growth'] = 'Not available in trial'
        df_f['med_age'] = 'Not available in trial'
        df_f['unemploy %'] = 'Not available in trial'
        df_f['family %'] = 'Not available in trial'
        df_f['college %'] = 'Not available in trial'
        df_f['vacancy'] = 'Not available in trial'
        df_f['poverty %'] = 'Not available in trial'

        df_f['price_to_rent_est_sqft'] = 'Not available in trial'
        df_f['price_to_rent_est_beds'] = 'Not available in trial'


    df_f = df_f.sort_values(by='price_to_rent',ascending=True)
    date = datetime.datetime.today()
    filename_result = 'results/' + city +'_filter_result_' + str(date) + '.csv'

    df_f.to_csv(filename_result, index=False)

    emailer.send_mail_gmail([email],'Madison Filter Results',subject='Madison Filter Results',attachment_path_list=[filename_result])
