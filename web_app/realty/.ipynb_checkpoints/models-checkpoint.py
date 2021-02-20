#  Copyright 2017 Google Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.postgres.fields import JSONField
from geopy.distance import distance
from googlemaps import Client


class Property(models.Model):

    PROPERTY_CAR_SPACES_CHOICES = [(i, i) for i in range(0, 4)]
    PROPERTY_BEDROOMS_CHOICES = [(i, i) for i in range(1, 5)]
    # PROPERTY_BATHROOMS_CHOICES = [(i, i) for i in range(0, 10)]
    PROPERTY_TYPE_CHOICES = (
        (1, 'All'),
        (2, 'SFH'),
        (3, "Condo"),
        (4, 'Duplex'),
        (5, 'Triplex'),
        (6, 'Quadruplex'),
        (7, '5+ Units')
    )

    ON_MARKET_CHOICES = (
        (0, 'Off'),
        (1, 'On')
    )

    class Meta:
        verbose_name_plural = "Properties"

    parcel = models.BigIntegerField(null=True)
    address = models.CharField(max_length=200,null=True)
    description = models.TextField()
    sqft = models.IntegerField(default=None,null=True)
    list_price = models.IntegerField(default=None,null=True)
    units = models.IntegerField(default=None, null=True)
    lot_size = models.FloatField(null=True)
    rent = models.CharField(default=None, max_length=250,null=True)
    taxes = models.FloatField(null=True)
    rent_estimate_beds = models.FloatField(default=None,null=True)
    rent_estimate_sqft = models.FloatField(default=None,null=True)
    year_built = models.IntegerField(default=None,null=True)
    growth_1 = models.FloatField(default=None,null=True)
    growth_3 = models.FloatField(default=None,null=True)
    growth_5 = models.FloatField(default=None,null=True)
    unemployed = models.FloatField(default=None,null=True)

    college = models.FloatField(default=None,null=True)
    vacancy = models.FloatField(default=None,null=True)
    # price_to_rent = models.CharField(default=None, max_length=250)
    price_to_rent = models.FloatField(default=None, max_length=250,null=True)

    price_to_rent_est_sqft = models.FloatField(default=None,null=True)
    price_to_rent_est_beds = models.FloatField(default=None,null=True)
    propertyType = models.CharField(null=True, max_length=60)
    family = models.FloatField(default=None,null=True)

    bedrooms = models.IntegerField(choices=PROPERTY_BEDROOMS_CHOICES, default=3,null=True)
    bathrooms = models.IntegerField(default=0, null=True)
    property_type = models.IntegerField(choices=PROPERTY_TYPE_CHOICES, default=1,null=True)
    nearest_school = models.CharField(max_length=1000, null=True)
    nearest_school_distance = models.FloatField(null=True)
    nearest_train_station = models.CharField(max_length=1000, null=True)
    nearest_train_station_distance = models.FloatField(null=True)
    point = models.PointField(srid=4326, null=True, unique=True)
    centralair = models.CharField(max_length=50, null=True)

    list_date = models.DateField(null=True)
    original_price = models.FloatField(null=True)
    one_cf = models.FloatField(null=True)

    transactions = JSONField(null=True)

    zoning = models.CharField(max_length=100, null=True)

    pfc = models.IntegerField(null=True)
    pfc_owner = models.CharField(max_length=75,null=True)
    pfc_date = models.CharField(max_length=50,null=True)

    new_build = models.IntegerField(null=True)
    nb_type = models.CharField(max_length=75,null=True)


    absentee = models.IntegerField(null=True)
    absent_owner = models.CharField(max_length=75,null=True)
    absent_owner_mail = models.CharField(max_length=150,null=True)
    absent_owner_city = models.CharField(max_length=50,null=True)
    absent_owner_state = models.CharField(max_length=10,null=True)
    absent_owner_zip = models.CharField(max_length=10,null=True)

    vacant = models.IntegerField(null=True)
    vacant_owner = models.CharField(max_length=75,null=True)
    vacant_owner_mail = models.CharField(max_length=150,null=True)
    vacant_owner_city = models.CharField(max_length=50,null=True)
    vacant_owner_state = models.CharField(max_length=10,null=True)
    vacant_owner_zip = models.CharField(max_length=10,null=True)


    car_spaces = models.IntegerField(choices=PROPERTY_CAR_SPACES_CHOICES, default=1,null=True)
    on_market = models.IntegerField(default=0, null=False, choices=ON_MARKET_CHOICES)

    def __str__(self):
        return self.address

    def set_google_maps_fields(self, latlng=None, calls=True):
        """
        Uses the Google Maps API to set:
          - geocoded latlng
          - nearest school name + distance
          - nearest train station name + distance
        """
        client = Client(key=settings.GOOGLE_MAPS_API_SERVER_KEY)
        if not latlng:
            data = client.geocode(self.address)
            if not data:
                raise Exception("Unable to resolve the address: '%s'" % address)
            latlng = data[0]["geometry"]["location"]
        self.point = GEOSGeometry("POINT(%(lng)s %(lat)s)" % latlng)

        if (calls):
            error = ""
            for field in ("school", "train_station"):
                try:
                    place = client.places_nearby(location=latlng, rank_by="distance", type=field)["results"][0]
                except IndexError:
                    continue
                except Exception as e:
                    error = e
                    continue
                setattr(self, "nearest_%s" % field, place["name"])
                place_latlng = place["geometry"]["location"]
                d = distance((latlng["lat"], latlng["lng"]), (place_latlng["lat"], place_latlng["lng"])).km
                setattr(self, "nearest_%s_distance" % field, round(d, 2))
            if error:
                raise Exception(error)


# class Transaction(models.Model):
#
#     property = models.ForeignKey(Property, max_length=50, related_name='transactions', on_delete=models.CASCADE)
#     parcel = models.BigIntegerField(max_length=100, null=True)
#     grantor = models.CharField(max_length=1000, null=True)
#     grantee = models.CharField(max_length=1000, null=True)
#     date = models.CharField(max_length=100, null=True)
#     price = models.CharField(max_length=50, null=True)
#     order = models.IntegerField(default=None, null=False)
