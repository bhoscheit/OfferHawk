# %%
import pandas as pd
from django.conf import settings
from django.core.management.base import BaseCommand
import googlemaps
import glob
import os
from django.contrib.gis.geos import GEOSGeometry
from realty.models import Property


# %%
class Command(BaseCommand):

    def load_props(number=-1,delete=True,transaction_flag=True, on_market_only=False):
        using_api = False
        filename = max(glob.iglob("/Users/bhoscheit/Desktop/OfferHawk/data_generation/staged_data_DB/properties" + "*.pkl"), key=os.path.getmtime)
        
        # load the file in
        print(filename)
        df_properties = pd.read_pickle(filename)
        print(df_properties.columns)

        df_properties = df_properties.where((pd.notnull(df_properties)), None)
        print(df_properties.at[0,'owner_absent'])

        df_properties['on_market'].fillna(0,inplace=True)
        df_properties['FullBaths'].fillna(0,inplace=True)
        df_properties['HalfBaths'].fillna(0,inplace=True)

        if (transaction_flag):
            df_trans = pd.read_csv('/Users/bhoscheit/Desktop/OfferHawk/data_generation/assessor_data/ownership_sale.csv')

        if delete:
            print("Deleting %s old properties" % Property.objects.count())
            Property.objects.all().delete()

        properties = []
        seen = set()

        if (on_market_only): df_properties = df_properties[df_properties['on_market']==1]

        random_sampling=False
        if (random_sampling):
            df_om_prop = df_properties[df_properties['on_market']==1]
            df_off_prop = df_properties[df_properties['on_market']==0]
            sample_off = df_off_prop.sample(frac=.10)
            df_properties=pd.concat([df_om_prop,sample_off])

        if number == -1 : number = len(df_properties)

        for i in df_properties.index[:number]:

            if (df_properties.at[i, 'on_market']==1):
                latlng = {
                    "lat": round(df_properties.at[i, 'lat'],5),
                    "lng": round(df_properties.at[i, 'lng'],5)
                }

                address = df_properties.at[i, 'address']

                property = Property(address=address)

                if (using_api):
                    property.set_google_maps_fields(latlng=latlng, calls=True)
                else:
                    property.point = GEOSGeometry("POINT(%(lng)s %(lat)s)" % latlng)

                if property.point.coords in seen:
                    print("Skipping duplicate location: %s" % address)
                    print("parcel: %s" % str(df_properties.at[i,'Parcel']))
                    continue

                seen.add((property.point.coords))

                property.sqft = df_properties.at[i, 'sqft']
                property.bedrooms = df_properties.at[i, 'beds']
                property.list_price = df_properties.at[i, 'list_price']
                property.rent = df_properties.at[i, 'rent']
                property.units = df_properties.at[i, 'units']
                if (property.units is None): property.units = df_properties.at[i,'TotalDwellingUnits']
                property.lot_size = df_properties.at[i, 'LotSize']
                property.taxes = df_properties.at[i,'TotalTaxes']
                property.rent_estimate_beds = df_properties.at[i, 'rent_estimate_beds']
                property.rent_estimate_sqft = df_properties.at[i, 'rent_estimate_sqft']
                property.year_built = df_properties.at[i, 'year_built']
                property.growth_1 = df_properties.at[i, '1yr growth']
                property.growth_2 = df_properties.at[i, '3yr growth']
                property.growth_3 = df_properties.at[i, '5yr growth']
                property.unemployed = df_properties.at[i, 'unemploy %']
                property.family = df_properties.at[i, 'family %']
                property.college = df_properties.at[i, 'college %']
                property.vacancy = df_properties.at[i, 'vacancy']
                property.price_to_rent = df_properties.at[i, 'price_to_rent']
                property.price_to_rent_est_sqft = df_properties.at[i, 'price_to_rent_est_sqft']
                property.price_to_rent_est_beds = df_properties.at[i, 'price_to_rent_est_beds']
                property.propertyType = df_properties.at[i, 'propType']
                property.property_type = df_properties.at[i, 'property_type']
                property.parcel = df_properties.at[i,'Parcel']
                property.zoning = df_properties.at[i,'ZoningAll']
                property.centralair = df_properties.at[i, 'CentralAir']
                property.bathrooms = df_properties.at[i, 'baths']
                property.on_market=1
                property.list_date = df_properties.at[i, 'list_date']
                property.original_price = df_properties.at[i, 'original_price']
                property.one_cf = df_properties.at[i, '1yr CF']
                property.pfc = df_properties.at[i,'pre_foreclosure']
                property.pfc_owner = df_properties.at[i,'owner name']
                property.pfc_date = df_properties.at[i,'filing date']
                property.absent_owner = df_properties.at[i,'owner_absent']
                property.absent_owner_mail = df_properties.at[i,'mailadd_absent']
                property.absent_owner_city =df_properties.at[i,'mail_city_absent']
                property.absent_owner_state =df_properties.at[i,'mail_state2_absent']
                property.absent_owner_zip =df_properties.at[i,'mail_zip_absent']

                if (property.absent_owner is not None):
                    property.absentee=1
                else:
                    property.absentee=0

                property.vacant_owner =df_properties.at[i,'owner_vacant']
                property.vacant_owner_mail =df_properties.at[i,'mailadd_vacant']
                property.vacant_owner_city =df_properties.at[i,'mail_city_vacant']
                property.vacant_owner_state =df_properties.at[i,'mail_state2_vacant']
                property.vacant_owner_zip =df_properties.at[i,'mail_zip_vacant']

                if (property.vacant_owner is not None):
                    property.vacant=1
                else:
                    property.vacant=0


                if (transaction_flag):
                    transactions = []
                    transaction_set = df_trans[df_trans['parcel']==property.parcel]

                    if (len(transaction_set) != 0):
                        for t in transaction_set.index:
                            transaction = {
                                'parcel':property.parcel,
                                'grantor':transaction_set.at[t,'grantor'],
                                'grantee':transaction_set.at[t, 'grantee'],
                                'date':transaction_set.at[t,'date'],
                                'price':transaction_set.at[t,'price'],
                                'order':transaction_set.at[t, 'order']
                            }
                            transactions.append(transaction)

                property.transactions=str(transactions)

                properties.append(property)

            elif (df_properties.at[i, 'new_build']==1):
                latlng = {
                    "lat": round(df_properties.at[i, 'lat'],5),
                    "lng": round(df_properties.at[i, 'lng'],5)
                }

                address = df_properties.at[i, 'address']

                property = Property(address=address)

                if (using_api):
                    property.set_google_maps_fields(latlng=latlng, calls=True)
                else:
                    property.point = GEOSGeometry("POINT(%(lng)s %(lat)s)" % latlng)

                if property.point.coords in seen:
                    print("Skipping duplicate location: %s" % address)
                    continue

                seen.add((property.point.coords))

                property.on_market = 0
                property.new_build = df_properties.at[i, 'new_build']
                property.nb_type = df_properties.at[i, 'build_type']

                properties.append(property)

            else :
                latlng = {
                    "lat": round(df_properties.at[i, 'latitude'],5),
                    "lng": round(df_properties.at[i, 'longitude'],5)
                }


                address = df_properties.at[i, 'Address']
                property = Property(address=address)

                if (using_api):
                    property.set_google_maps_fields(latlng=latlng, calls=True)
                else:
                    property.point = GEOSGeometry("POINT(%(lng)s %(lat)s)" % latlng)

                if property.point.coords in seen:
                    print("Skipping duplicate location: %s" % address)
                    continue

                seen.add((property.point.coords))

                property.zoning = df_properties.at[i, 'ZoningAll']
                property.sqft = df_properties.at[i, 'TotalLivingArea']
                property.units = df_properties.at[i,'TotalDwellingUnits']
                property.lot_size = df_properties.at[i, 'LotSize']
                property.year_built = df_properties.at[i, 'MaxConstructionYear']
                property.centralair = df_properties.at[i, 'CentralAir']
                property.parcel = df_properties.at[i,'Parcel']
                property.taxes = df_properties.at[i,'TotalTaxes']
                property.propertyType = df_properties.at[i, 'propType']
                property.property_type = df_properties.at[i, 'property_type']
                property.bathrooms = df_properties.at[i, 'FullBaths'] + df_properties.at[i, 'HalfBaths']
                property.on_market=0
                property.pfc = df_properties.at[i,'pre_foreclosure']
                property.pfc_owner = df_properties.at[i,'owner name']
                property.pfc_date = df_properties.at[i,'filing date']
                property.absent_owner = df_properties.at[i,'owner_absent']
                property.absent_owner_mail = df_properties.at[i,'mailadd_absent']
                property.absent_owner_city =df_properties.at[i,'mail_city_absent']
                property.absent_owner_state =df_properties.at[i,'mail_state2_absent']
                property.absent_owner_zip =df_properties.at[i,'mail_zip_absent']
                property.vacant_owner =df_properties.at[i,'owner_vacant']
                property.vacant_owner_mail =df_properties.at[i,'mailadd_vacant']
                property.vacant_owner_city =df_properties.at[i,'mail_city_vacant']
                property.vacant_owner_state =df_properties.at[i,'mail_state2_vacant']
                property.vacant_owner_zip =df_properties.at[i,'mail_zip_vacant']

                if (transaction_flag):
                    transactions = []
                    transaction_set = df_trans[df_trans['parcel']==property.parcel]

                    if (len(transaction_set) != 0):
                        for t in transaction_set.index:
                            transaction = {
                                'parcel':property.parcel,
                                'grantor':transaction_set.at[t,'grantor'],
                                'grantee':transaction_set.at[t, 'grantee'],
                                'date':transaction_set.at[t,'date'],
                                'price':transaction_set.at[t,'price'],
                                'order':transaction_set.at[t, 'order']
                            }
                            transactions.append(transaction)

                property.transactions=str(transactions)

                properties.append(property)
                print("Resolved %s" % address)


        Property.objects.bulk_create(properties,batch_size=3000)

        print("Inserted %s properties" % len(properties))

    def handle(self, **options):
        using_api = False
        on_market = False
        test = 10000

        print('Server key: ' + str(settings.GOOGLE_MAPS_API_SERVER_KEY))
        client = googlemaps.Client(key=settings.GOOGLE_MAPS_API_SERVER_KEY)

        Command.load_props()
