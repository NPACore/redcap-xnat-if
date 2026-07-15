#!/usr/bin/env python

import redcap
import requests
import os
from dotenv import load_dotenv
from urllib.parse import urlparse
from datetime import date


def normalize_id(s):
    """Ameliorate label inconsistencies.
    Make REDCap survey to xNAT match more likely by removing punctuation and case."""
    return s.upper().replace("_", "").replace("-", "").replace(" ", "")


def error_dict(record, msg):
    """
    Dict for REDCap with failed message and current date.
    """
    # TODO: track date range with in sync date like 'first,today' ?
    # find first each time like: min(record['xnat_sync_date'].split(','))
    return {
        "record_id": record["record_id"],
        "xnat_sync_status": f"failed - {msg}",
        "xnat_sync_date": date.today().strftime("%Y-%m-%d"),
    }


def redcap_to_xnat(record, xnat) -> dict:
    """ """
    xnat_url = record["xnat_url"]
    subject = record["subj_id"]
    session = record["ses_id"]

    BASE_URL = os.getenv("XNAT_URL")
    # TODO!!: need to search w/o knowing xnat project name!
    XNAT_PROJECT = os.getenv("XNAT_PROJECT")

    if not subject:
        print(f"  Skipping record {record['record_id']} - missing subj_id")
        return error_dict(record, "no subj_id in REDCap")

    scan_date = record["scan_date"]

    # TODO: check xnat url can get session and date from that
    if not session and not scan_date:
        print(
            f"  Skipping record {record['record_id']} - need either ses_id or scan_date"
        )
        return error_dict(record, "no xnat info REDCap")

    finding = record["finding"]
    # TODO: allow key error if field doesn't exist.
    #       all records should have this field even if empty.
    #        big problem if MIA. Should fail, not silently continue
    action = record.get("follow_needed", "")
    review_date = record.get("req_date", "")
    session_url = xnat_url

    print(f"Processing record {record['record_id']} - {subject}/{session}")

    # TODO!!: find xnat project. maybe using session search, URL, or redcap project

    # get experiment ID from label
    experiments_url = f"{BASE_URL}/data/projects/{XNAT_PROJECT}/subjects/{subject}/experiments?format=json"
    r = xnat.get(experiments_url)

    if r.status_code != 200:
        print(f"  Could not find subject {subject} in XNAT {r.status_code}, skipping")
        return error_dict(record, f"xnat lookup {r.status_code}")

    results = r.json()["ResultSet"]["Result"]

    # initialize so we can test various ways to find the session
    match = None
    # if only session ID, match by label
    if session:
        match = next(
            (e for e in results if normalize_id(e["label"]) == normalize_id(session)),
            None,
        )
    # otherwise fall back to scan_date
    # TODO: 'if not match' instead of 'else'.
    #        possibly given bad sesid
    else:
        match = next((e for e in results if e.get("date") == scan_date), None)

    # TODO: additional 'if not match' to try using getting session from xnat url

    if not match:
        print(
            f"  WARNING: No matching session found for {subject} - bad session ID or not uploaded yet. Skipping."
        )
        return error_dict(record, "no xnat match")

    experiment_id = match["ID"]

    if not experiment_id:
        print(f"  Could not find experiment for session {session}, skipping")
        return error_dict(record, f"no experiment for session {session}")

    print(f"  Experiment ID: {experiment_id}")

    # push to session-level custom form
    session_endpoint = f"{BASE_URL}/xapi/custom-fields/projects/{XNAT_PROJECT}/subjects/{subject}/experiments/{experiment_id}/fields"
    session_payload = {
        SESSION_FORM_UUID: {
            "finding": finding,
            "action_required": action,
            "review_date": review_date,
        }
    }
    r = xnat.put(session_endpoint, json=session_payload)
    print(f"  Session form: {r.status_code}")

    # push flag to subject-level custom form
    subject_endpoint = f"{BASE_URL}/xapi/custom-fields/projects/{XNAT_PROJECT}/subjects/{subject}/fields"
    subject_payload = {
        SUBJECT_FORM_UUID: {"ifr_flag": "True", "session_link": session_url}
    }
    r = xnat.put(subject_endpoint, json=subject_payload)
    print(f"  Subject flag: {r.status_code}")

    # after both 200 responses
    return {
        "record_id": record["record_id"],
        "xnat_sync_status": "synced",
        "xnat_sync_date": date.today().strftime("%Y-%m-%d"),
        "xnat_ses_id_cron": match["label"],
        "xnat_url_cron": f"{BASE_URL}/data/projects/{XNAT_PROJECT}/subjects/{subject}/experiments/{experiment_id}",
    }


def main():
    """Run sync for all surveys"""

    # populate os.environ. load_dotenv false if no .env file
    # assume if manually set REDCAP_TOKEN, can figure out other settings
    if not load_dotenv() and not os.getenv("REDCAP_TOKEN"):
        raise Exception("Mssing .env file with REDCap and XNAT credentials")

    # connections
    project = redcap.Project(os.getenv("REDCAP_URL"), os.getenv("REDCAP_TOKEN"))

    xnat = requests.Session()
    xnat.auth = (os.getenv("XNAT_USER"), os.getenv("XNAT_PASS"))

    SESSION_FORM_UUID = os.getenv("XNAT_FORM_UUID")
    SUBJECT_FORM_UUID = os.getenv("XNAT_SUBJECT_FORM_UUID")

    # pull completed reveiw from REDcap
    records = project.export_records(
        filter_logic='[report_complete] = "2" AND [xnat_sync_status] != "synced"'
    )
    print(f"Found {len(records)} completed review")

    for record in records:
        sync_record = redcap_to_xnat(record)

        if os.getenv("DRYRUN"):
            print(sync_record)
        else:
            # TODO: sync all at onces. build array to submit instead of request per row?
            project.import_records([sync_record])
        print(f"  REDCap sync status updated")

    print("Done.")


if __name__ == "__main__":
    main()
