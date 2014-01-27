from ccu_gen_beta.models import *
from ccu_utilities import stateAbbrevs,districts

#just create state names in db
def createStates(): 
    for stateAbbrev,stateName in stateAbbrevs.items():
        stateObj = State.objects.get_or_create(abbrev=stateAbbrev,name=stateName)

#after creating state names, simply enumerate districts
def createDistricts():
    for stateName,districtNum in districts.items():
        stateObj = State.objects.get(name=stateName)
        if districtNum==0:
            districtObj = District.objects.get_or_create(state=stateObj,districtNum=0)
        else:
            for i in range(1,districtNum+1):
                districtObj = District.objects.get_or_create(state=stateObj,districtNum=i)

if __name__ == '__main__':
    #District.objects.all().delete()
    createDistricts()
    pass