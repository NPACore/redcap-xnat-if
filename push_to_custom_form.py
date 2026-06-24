#!/usr/bin/env python
import requests
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv('XNAT_URL')
USER = os.getenv('XNAT_USER')
PASS = os.getenv('XNAT_PASS')
FORM_UUID = os.getenv('XNAT_FORM_UUID')

# get session token
session = requests.Session()
session.auth = (USER, PASS)

# test data matching TEST_SESSION_001
payload = {
        FORM_UUID: {
            "finding": "test finding",
            "action_required": "let subject know",
            "review_date": "2026-06-23"
        }
}

# push to session
project = 'Test_Project'
subject = 'TEST_SUBJECT_001'
experiment = 'TEST_SESSION_001'

url = f"{BASE_URL}/xapi/custom-fields/projects/{project}/subjects/{subject}/experiments/{experiment}/fields"

#response = session.get(url)
#print(f"Status: {response.status_code}")
#print(response.json())
response = session.put(url, json=payload)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
