#!/usr/bin/env python
import requests
import os
from dotenv import load_dotenv

load_dotenv()

xnat = requests.Session()
xnat.auth = (os.getenv('XNAT_USER'), os.getenv('XNAT_PASS'))

BASE_URL = os.getenv('XNAT_URL')

r = xnat.get(f"{BASE_URL}/data/projects/Test_Project/subjects/TEST_SUBJECT_001/experiments?format=json")
print(r.json())
