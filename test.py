from BinaryOptionsTools import pocketoption
from BinaryOptionsTools.indicators.momentum import *

ssid = (r'42["auth",{"session":"vtftn12e6f5f5008moitsd6skl","isDemo":1,"uid":27658142,"platform":1}]')
api = pocketoption(ssid, True)
print(api.GetBalance())

print(roc(api, 60, "EURUSD_otc", 14))