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
session = subject.experiment('TEST_SESSION_001')

scan = session.scan('1')
scan.create(**{'xnat:mrScanData/type': 'localizer'})

# upload the dicom files
dicom_dir = 'test_dicoms/localizer'
resource = scan.resource('DICOM')
resource.create()

for f in os.listdir(dicom_dir):
    if f.endswith('.dcm'):
        filepath = f'{dicom_dir}/{f}'
        print(f"Uploading {f}...")
        resource.file(f).insert(filepath)
        print("Done.")
