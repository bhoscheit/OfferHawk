import re

class City(object):

    def __init__(self, name):
        self.name = name

    def setAreaZ(self,areas):
        self.areaZ = areas

    def getAreaZ(self):
        return self.areaZ

    def setAreaH(self,areas):
        self.areaH = areas

    def getAreaH(self):
        return self.areaH

    def setZips(self,zips):
        self.zips = zips

    def getZips(self):
        return self.zips

    def getName(self):
        return self.name

    def setWindows(self, windows):
        self.windows = windows

    def getWindows(self):
        return self.windows

    def parseRent(self,data):
        print('Default parser')
        return


class Madison(City):

    def __init__(self, name, city):
        self.name = name
        self.areaZ = city.areaZ
        self.areaH = city.areaH
        self.zips = city.zips

    def parseRent(self, details):
        tot_mo_rent = 0
        tot_total_inc = 0

        for fact in details['Details']:

            if (re.match('Unit (\d+)',fact['Name'])):
                for field in fact['Fields']:
                    if ('Mo Rent' in field['Name']):
                        tot_mo_rent+=float(field['Value'])
                    elif ('Monthly Rent' in field['Name']):
                        tot_mo_rent+=float(field['Value'])

            if (('Rental Info' in fact['Name'])):
                for field in fact['Fields']:
                    if ('Total Income' in field['Name']):
                        tot_total_inc+=float(field['Value'])

        mo_rent_12 = tot_mo_rent * 12
        if (tot_total_inc > mo_rent_12):
            tot = tot_total_inc/12
        else:
            tot = tot_mo_rent

        return tot
