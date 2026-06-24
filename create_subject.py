import pyxnat
import os
from dotenv import load_dotenv

load_dotenv()

xnat = pyxnat.Interface(
        server='http://10.48.86.97',
        user=os.getenv('XNAT_USER'),
        password=os.getenv('XNAT_PASS')
)

subject = xnat.select.project('Test_Project').subject('TEST_SUBJECT_001')
subject.create()
print(f"Subject exists: {subject.exists()}")

session = subject.experiment('TEST_SESSION_001')
session.create(**{'xnat:mrSessionData/date': '2026-06-23'})
print(f"Session exists: {session.exists()}")
