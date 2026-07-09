#!/usr/bin/env python
import requests
import os
from dotenv import load_dotenv

load_dotenv()

xnat = requests.Session()
xnat.auth = (os.getenv('XNAT_USER'), os.getenv('XNAT_PASS'))

BASE_URL = os.getenv('XNAT_URL')

r = xnat.get(f"{BASE_URL}/xapi/custom-fields/projects/Test_Project/subjects/TEST_SUBJECT_001/fields")
import json
print(json.dumps(r.json(), indent=2))
