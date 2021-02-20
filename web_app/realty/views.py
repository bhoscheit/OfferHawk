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

from django.contrib.gis.geos import GEOSGeometry, Polygon
from django.core.serializers import serialize
from django.conf import settings
from django.db import connection
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
import json
from .models import Property


def properties_geojson(request):

    """
    Retrieves properties given the querystring params, and
    returns them as GeoJSON.
    """
    ne = request.GET["ne"].split(",")
    sw = request.GET["sw"].split(",")

    types = request.GET["property-types"].split(",")
    om = request.GET['on-market']
    yb = request.GET['year-built']
    zoom = request.GET['zoom']
    offm = request.GET['off-market']
    pfc = request.GET['pfc']
    nb = request.GET['new-construction']
    vac = request.GET['vacant']
    abs = request.GET['absentee']

    lookup = {
        "point__contained": Polygon.from_bbox((sw[1], sw[0], ne[1], ne[0]))
        # "bedrooms__gte": request.GET["min-bedrooms"],
        # "bedrooms__lte": request.GET["max-bedrooms"]
        # "bathrooms__gte": request.GET["min-bathrooms"],
        # "car_spaces__gte": request.GET["min-car-spaces"],

    }
    # if request.GET["nearest-school"] != "1":
    #     lookup["nearest_school_distance__lt"] = int(request.GET["nearest-school"]) - 1

    if request.GET["smallest-ptr"] != "0":
        lookup["price_to_rent__lt"] = int(request.GET["smallest-ptr"])

    # if (request.user.is_staff):
    if request.GET["smallest-ptr-b"] != "0":
        lookup["price_to_rent_est_beds__lt"] = int(request.GET["smallest-ptr-b"])

    if types[0] != '1':
        lookup["property_type__in"] = types

    if yb != '1836':
        lookup["year_built__gte"] = int(yb)

    lookup_offm_pfc = dict(lookup)
    lookup_offm_nb = dict(lookup)
    lookup_offm = dict(lookup)

    if om == '1':
        lookup["on_market__exact"] = om
    else:
        lookup["on_market__exact"] = '-1'

    if ((offm=='1') & (pfc == '1')):
        lookup_offm_pfc["pfc__exact"] = 1
    else:
        lookup_offm_pfc["on_market__exact"] = '-1'


    if ((offm=='1') & (nb == '1')):
        lookup_offm_nb["new_build__exact"] = 1
    else:
        lookup_offm_nb["on_market__exact"] = '-1'

    if ((pfc != '1') & (nb != '1')):
        if ((offm == '1') & (int(zoom) >= 17)):
            lookup_offm["on_market__exact"] = '0'
        elif ((offm == '1') & (abs == '1' or vac == '1')):
            lookup_offm["on_market__exact"] = '0'
        else:
            lookup_offm["on_market__exact"] = '-1'
    else:
        lookup_offm['on_market__exact'] = '-1'

    if (vac == '1'):
        lookup['vacant__exact'] = 1
        lookup_offm['vacant__exact'] = 1
        lookup_offm_nb['vacant__exact'] = 1
        lookup_offm_pfc['vacant__exact'] = 1

    if (abs == '1'):
        lookup['absentee__exact'] = 1
        lookup_offm['absentee__exact'] = 1
        lookup_offm_nb['absentee__exact'] = 1
        lookup_offm_pfc['absentee__exact'] = 1

    properties_on = Property.objects.filter(**lookup)
    properties_off = Property.objects.filter(**lookup_offm)
    properties_pfc = Property.objects.filter(**lookup_offm_pfc)
    properties_nb = Property.objects.filter(**lookup_offm_nb)
    properties = properties_on.union(properties_off, properties_pfc, properties_nb, all=True)

    json_data = serialize("geojson", properties, geometry_field="point")

    return HttpResponse(json_data, content_type="application/json")


def properties_map(request):
    """
    Index page for the app, with map + form for filtering
    properties.
    """
    print(request.user)
    
    # if (not request.user.is_authenticated):
    #     print('User is not authenticated')
    #     return redirect('%s?next=%s' % ('/login', request.path))
        # return redirect('/admin/')
        # redirect('myapp/login_error.html')
        # return render(request, 'admin')

    # Get the center of all properties, for centering the map.

    if Property.objects.exists():
        cursor = connection.cursor()
        cursor.execute("SELECT ST_AsText(st_centroid(st_union(point))) FROM realty_property")
        center = dict(zip(("lng", "lat"), GEOSGeometry(cursor.fetchone()[0]).get_coords()))
    else:
        # Default, when no properties exist.
        center = {"lat": -33.864869, "lng": 151.1959212}

    context = {
        "center": json.dumps(center),
        "title": "Property Finder",
        "api_key": settings.GOOGLE_MAPS_API_WEB_KEY,
        "property_types": Property._meta.get_field("property_type").choices,
        # "on-market": Property._meta.get_field("on-market").choices,
        "distance_range": (1, 21),
        "ptr_range": (0,20),
        "year_built_range": (1836, 2019)
    }

    # Ranges for each of the slider fields.
    # for field in ["bedrooms", "bathrooms", "car_spaces"]:
    #     choices = Property._meta.get_field("bedrooms").choices
    #     context[field + "_range"] = (choices[0][0], choices[-1][0])
    # return render(request, "login.html")
    # print(request)
    return render(request, "map.html", context)
