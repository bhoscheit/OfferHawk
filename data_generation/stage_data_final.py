# %%
import pandas as pd
from io import StringIO
import numpy as np
import glob
import geopy.distance
import datetime
import os

# %%
username = os.environ.get('DB_USER')
password = os.environ.get('DB_PASS')

def loadDB():

    from sqlalchemy import create_engine
    from sqlalchemy import event
    engine = create_engine('postgresql://' + str(username) + ':' + str(password) + '@34.66.99.154:5432/madison')

    def to_sql(engine, df, table, if_exists='fail', sep='\t', encoding='utf8'):
        # Create table
        df[:0].to_sql(table, engine, if_exists=if_exists)

        # Prepare data
        output = StringIO()
        df.to_csv(output, sep=sep, header=False, encoding=encoding)
        output.seek(0)

        # Insert data
        connection = engine.raw_connection()
        cursor = connection.cursor()
        cursor.copy_from(output, table, sep=sep, null='')
        connection.commit()
        cursor.close()

    conn = engine.connect()

    # static data for web app
    df_trans = pd.read_csv('assessor_data/ownership_sale.csv')
    df_assess_raw = pd.read_json('assessor_data/data.json')
    df_construction = pd.read_csv('construction/new_recent_builds_madison_jun_thru_aug_2019.csv')
    filename = max(glob.iglob("staged_data/Madison_" + "*.pkl"), key=os.path.getmtime)
    
    # load the file in
    print(filename)
    df_filter = pd.read_pickle(filename)
    df_filter['parcel']=None
    df_map = pd.read_sql('address_map', conn)

    geometry = []
    properties = []
    for i in df_assess_raw.index:
        geometry.append(df_assess_raw['features'].at[i]['geometry'])
        properties.append(df_assess_raw['features'].at[i]['properties'])

    df_assessor = pd.DataFrame.from_records(properties)

    lat = []
    long = []
    for crds in geometry:
        temp = np.array(crds['coordinates'][0])
        mean = np.mean(temp, axis=0)
        lat.append(mean[1])
        long.append(mean[0])

    df_assessor['latitude'] = lat
    df_assessor['longitude'] = long

    # get the formatted addresses
    formatted_addresses = []
    for address in df_filter['address'].str.split(',').apply(lambda x: x[0]):
        words = address.split(' ')
        for i, word in enumerate(words):
            for m in df_map.index:
                if(word == df_map.at[m,'input']):
                    words[i] = df_map.at[m,'output']

            if (i == len(words) - 1):
                if (word[0] == '#'):
                    words[i] = 'Unit ' + word[1:]
        formatted_addresses.append(' '.join(words))

    # convert n, s, e, w to abbreviations in assessor data
    formatted_addresses_assessor = []
    for address in df_assessor['Address']:
        words = address.split(' ')
        if (words[1] == 'North'):
            words[1] = 'N'
        elif (words[1] == 'South'):
            words[1] = 'S'
        elif (words[1] == 'East'):
            words[1] = 'E'
        elif (words[1] == 'West'):
            words[1] = 'W'
        formatted_addresses_assessor.append(' '.join(words))
    df_assessor['formatted_address'] = formatted_addresses_assessor

    # get the parcel numbers based on lat long distance
    counts = []
    error_tolerance = 0.003
    for i in df_filter.index:
        lat = df_filter.at[i,'lat']
        lng = df_filter.at[i,'lng']
        lat_lng = (lat, lng)
        address = df_filter.at[i,'address']
        df_possible_addresses = df_assessor[(df_assessor['latitude'] >= lat - error_tolerance) &
                                        (df_assessor['latitude'] <= lat + error_tolerance) &
                                        (df_assessor['longitude'] >= lng - error_tolerance) &
                                        (df_assessor['longitude'] <= lng + error_tolerance)]

        # find the nearest properties in the city data set
        distances = []
        for j in df_possible_addresses.index:
            lat_lng_tar = (df_possible_addresses.at[j,'latitude'],df_possible_addresses.at[j,'longitude'])
            dist = geopy.distance.distance(lat_lng, lat_lng_tar).km
            distances.append((j,dist))
        distances = sorted(distances,key=lambda x: x[1])

        if (len(distances)==0): continue

        # iterate through the nearest properties up to max_retries times to find a match
        parcel=None
        retry = 0
        max_retries = len(distances)
        while retry < max_retries:
            # get the closest by distance
            index_possible = distances[retry][0]
            possible_address = df_possible_addresses.loc[index_possible]['formatted_address']
            if ((address.split(' ')[0] == possible_address.split(' ')[0]) & (address.split(' ')[1] == possible_address.split(' ')[1])):
                parcel = df_possible_addresses.loc[index_possible, 'Parcel']
                df_filter.at[i,'parcel'] = parcel
                break
            retry += 1

    df_filter['on_market']=1
    df_final = pd.merge(df_filter,df_assessor,left_on='parcel',right_on='Parcel',how='outer')
    df_final['price_to_rent'][df_final['price_to_rent']==np.inf]=None
    df_final['price_to_rent_est_sqft'][df_final['price_to_rent_est_sqft']==np.inf]=None
    df_final['price_to_rent_est_beds'][df_final['price_to_rent_est_beds']==np.inf]=None
    df_final['Parcel'].fillna(0,inplace=True)
    df_final['Parcel'] = df_final['Parcel'].astype('int')

    # SFH
    df_final.loc[(df_final['PropertyUseCode']==1) & (df_final['PropertyClass']=='Residential'),'propType']='SFH'
    # condo
    df_final.loc[(df_final['PropertyUseCode']==2) & (df_final['PropertyClass']=='Residential'),'propType']='Condo'
    # duplex
    df_final.loc[(df_final['TotalDwellingUnits']==2),'propType']='Duplex'
    # tri
    df_final.loc[(df_final['TotalDwellingUnits']==3),'propType']='Triplex'
    # quad
    df_final.loc[(df_final['TotalDwellingUnits']==4),'propType']='Quadruplex'
    # 5+
    df_final.loc[(df_final['TotalDwellingUnits']>=5),'propType']='5+ Units'

    # SFH
    df_final.loc[(df_final['propType'] == 'SFH'),'property_type'] = 2
    # condo
    df_final.loc[(df_final['propType'] == 'Condo'),'property_type'] = 3
    # duplex
    df_final.loc[(df_final['propType'] == 'Duplex'),'property_type'] = 4
    # tri
    df_final.loc[(df_final['propType'] == 'Triplex'),'property_type'] = 5
    # quad
    df_final.loc[(df_final['propType'] == 'Quadruplex'),'property_type'] = 6
    # 5+
    df_final.loc[(df_final['propType'] == '5+ Units'),'property_type'] = 7

    df_construction.rename(columns={'long':'lng','type':'build_type'}, inplace=True)
    df_final = pd.concat([df_final, df_construction], sort=False)
    df_final.reset_index(inplace=True)
    df_final.loc[df_final['build_type'].notnull(),'new_build'] = 1

    df_vacant = pd.read_csv('vacancy_absentee/madison_vacant_properties_nov_2019_red2_mail.csv')
    df_absent = pd.read_csv('vacancy_absentee/madison_absentee_owner_properties_nov_2019_red_mail.csv')

    df_vacant['parcelnumb'] = df_vacant['parcelnumb'].astype(float).astype(str)
    df_absent['parcelnumb'] = df_absent['parcelnumb'].astype(float).astype(str)

    cols_v = []
    for col in df_vacant.columns:
         cols_v.append(col + '_vacant')

    cols_a = []
    for col in df_absent.columns:
        cols_a.append(col + '_absent')

    df_vacant.columns = cols_v
    df_absent.columns = cols_a

    df_absent['mail_zip_absent'].astype(str, inplace=True)
    df_vacant['mail_zip_vacant'].astype(str, inplace=True)

    df_v = pd.merge(df_properties,df_vacant,left_on='Parcel',right_on='parcelnumb_vacant',how='left')
    df_a_v = pd.merge(df_v,df_absent,left_on='Parcel',right_on='parcelnumb_absent',how='left')

    df_a_v['Parcel'] = df_a_v['Parcel'].astype(float)

    df_a_v.to_pickle('staged_data_DB/properties' + str(datetime.datetime.now().date()) + '.pkl')

    os.chdir('/Users/bhoscheit/Desktop/OfferHawk/web_app/')
    os.system('source /Users/bhoscheit/.bashrc && python manage.py populate_madison')


if __name__ == '__main__':
    loadDB()
