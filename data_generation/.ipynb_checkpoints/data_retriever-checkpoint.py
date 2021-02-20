import hsdata
import time
import requests
import zillowdata
import filterf
import stage_data_final
import os

# +
name_m = 'Madison'
counties = ['Dane','Columbia','Dodge','Green','Iowa','Jefferson','Lafayette','Rock','Sauk']
for county in counties:
    print(county)
    try:
        hsdata.ingestData(county)
    except requests.exceptions.ConnectionError:
        time.sleep(300)
        hsdata.ingestData(county)

    zillowdata.ingestRentalData(county)
    hsdata.updateZips(county)
    zillowdata.updateZips(county)
    filterf.stageData(county)
    
filterf.combineFilters(counties, name_m)
