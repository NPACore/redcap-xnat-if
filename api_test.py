#!/usr/bin/env python
import requests
import os
from dotenv import load_dotenv
load_dotenv()
data = {
        'token' : os.getenv('REDCAP_TOKEN'),
        'content' : 'project',
        'format' : 'json',
        'returnFormat' : 'json'
}
r = requests.post('https://redcap-std.hs.pitt.edu/redcap/api/', data=data)
print('HTTP Status: ' + str(r.status_code))
print(r.json())
