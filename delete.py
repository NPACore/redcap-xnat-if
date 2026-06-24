#!/usr/bin/env python
import pyxnat
import os
from dotenv import load_dotenv

load_dotenv()

xnat = pyxnat.Interface(
    server='http://10.48.86.97',
    user=os.getenv('XNAT_USER'),
    password=os.getenv('XNAT_PASS')
)

xnat.select.project('Test_Project').subject('TEST_SUBJECT_002').delete()
print("Deleted.")
