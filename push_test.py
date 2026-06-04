#!/usr/bin/env python
import redcap
import os
from dotenv import load_dotenv

load_dotenv()

URL = 'https://redcap-std.hs.pitt.edu/redcap/api/'
TOKEN = os.getenv('REDCAP_TOKEN')

project = redcap.Project(URL, TOKEN)

new_record = [{
    'record_id': '0', 
    'pi': 'TestPI',
    'bill_code': 'WPC-1234',
    'ses_id': 'SUB001',
    'xnat_url': 'https://xnat.example.com/session/123',
    'scan_time': '2026-06-01 10:00',
    'found_time': '2025-06-01 10:30',
    'alert_email': 'hudlowe@pitt.edu',
    'viewer_email': 'hudlowe@pitt.edu',
    'request_complete': '2'
}]

response = project.import_records(new_record, force_auto_number=True)
print("Response:", response)
