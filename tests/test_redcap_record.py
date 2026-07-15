"""
Exercise redcap_xnat
"""

from redcap_xnat import redcap_to_xnat

record = {"record_id": 1, "xnat_url": "", "subj_id": "XYZ", "ses_id": "ABC"}


def test_record_nosubj():
    ret = redcap_to_xnat({**record, "subj_id": ""}, xnat=None)
    assert ret.get("xnat_sync_status") == "failed - no subj_id in REDCap"
