#!/usr/bin/env python

import redcap
import requests
import os
from dotenv import load_dotenv
from urllib.parse import urlparse
from datetime import date

load_dotenv()

# connections
project = redcap.Project(os.getenv('REDCAP_URL'), os.getenv('REDCAP_TOKEN'))

xnat = requests.Session()
xnat.auth = (os.getenv('XNAT_USER'), os.getenv('XNAT_PASS'))

BASE_URL = os.getenv('XNAT_URL')
XNAT_PROJECT = os.getenv('XNAT_PROJECT')
SESSION_FORM_UUID = os.getenv('XNAT_FORM_UUID')
SUBJECT_FORM_UUID = os.getenv('XNAT_SUBJECT_FORM_UUID')

def normalize_id(s):
    return s.upper().replace('_', '').replace('-', '').replace(' ', '')

# pull completed reveiw from REDcap
records = project.export_records(filter_logic='[report_complete] = "2" AND [xnat_sync_status] != "synced"')
print(f"Found {len(records)} completed review")

for record in records:
    xnat_url = record['xnat_url']
    subject = record['subj_id']
    session = record['ses_id']

    if not subject:
        print(f"  Skipping record {record['record_id']} - missing subj_id")
        continue

    scan_date = record['scan_date']
    
    if not session and not scan_date:
        print(f"  Skipping record {record['record_id']} - need either ses_id or scan_date")
        continue

    finding = record['finding']
    action = record.get('follow_needed', '')
    review_date = record.get('req_date', '')
    session_url = xnat_url

    print(f"Processing record {record['record_id']} - {subject}/{session}")

    # get experiment ID from label
    experiments_url = f"{BASE_URL}/data/projects/{XNAT_PROJECT}/subjects/{subject}/experiments?format=json"
    r = xnat.get(experiments_url)
    
    if r.status_code != 200:
        print(f"  Could not find subject {subject} in XNAT, skipping")
        continue
    
    results = r.json()['ResultSet']['Result']

    # if only session ID, match by label
    if session:
        match = next((e for e in results if normalize_id(e['label']) == normalize_id(session)), None)
    # otherwise fall back to scan_date
    else:
        match = next((e for e in results if e.get('date') == scan_date), None)

    if not match:
        print(f"  WARNING: No matching session found for {subject} - bad session ID or not uploaded yet. Skipping.")
        continue

    experiment_id = match['ID']

    if not experiment_id:
        print(f"  Could not find experiment for session {session}, skipping")
        continue

    print(f"  Experiment ID: {experiment_id}")
    
    # push to session-level custom form
    session_endpoint = f"{BASE_URL}/xapi/custom-fields/projects/{XNAT_PROJECT}/subjects/{subject}/experiments/{experiment_id}/fields"
    session_payload = {
        SESSION_FORM_UUID: {
            "finding": finding,
            "action_required": action,
            "review_date": review_date
        }
    }
    r = xnat.put(session_endpoint, json=session_payload)
    print(f"  Session form: {r.status_code}")

    # push flag to subject-level custom form
    subject_endpoint = f"{BASE_URL}/xapi/custom-fields/projects/{XNAT_PROJECT}/subjects/{subject}/fields"
    subject_payload = {
        SUBJECT_FORM_UUID: {
            "ifr_flag": "True",
            "session_link": session_url
        }
    }
    r = xnat.put(subject_endpoint, json=subject_payload)
    print(f"  Subject flag: {r.status_code}")

    # after both 200 responses
    sync_record = [{
        'record_id': record['record_id'],
        'xnat_sync_status': 'synced',
        'xnat_sync_date': date.today().strftime('%Y-%m-%d'),
        'xnat_ses_id_cron': match['label'],
        'xnat_url_cron': f"{BASE_URL}/data/projects/{XNAT_PROJECT}/subjects/{subject}/experiments/{experiment_id}"
        }]
    project.import_records(sync_record)
    print(f"  REDCap sync status updated")

print("Done.")
