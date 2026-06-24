#!/usr/bin/env python
import flywheel
import pyxnat
import pydicom
import zipfile
import os
import shutil
from dotenv import load_dotenv

load_dotenv()

# connections
fw = flywheel.Client(os.getenv('FW_API_KEY'))
xnat = pyxnat.Interface(
    server='http://10.48.86.97',
    user=os.getenv('XNAT_USER'),
    password=os.getenv('XNAT_PASS')
)

# config
XNAT_PROJECT = 'Test_Project'
N_SESSIONS = 5
WORK_DIR = 'test_dicoms'
os.makedirs(WORK_DIR, exist_ok=True)

# get 5 most recent sessions
project = fw.lookup('mrrc/Prisma1QA')
sessions = sorted(project.sessions(), key=lambda s: s.timestamp, reverse=True)[:N_SESSIONS]

for i, ses in enumerate(sessions, start=2):  # start=2 since 001 already exists
    subject_label = f'TEST_SUBJECT_{i:03d}'
    session_label = f'TEST_SESSION_{i:03d}'
    print(f"\nProcessing {ses.label} → {subject_label}/{session_label}")

    # create subject and session in XNAT
    subject = xnat.select.project(XNAT_PROJECT).subject(subject_label)
    subject.create()
    session = subject.experiment(session_label)
    session.create(**{'xnat:mrSessionData/date': ses.timestamp.strftime('%Y-%m-%d')})

    # process each acquisition
    for acq in ses.acquisitions():
        for f in acq.files:
            if f.type != 'dicom':
                continue

            print(f"  Downloading {acq.label}...")
            acq_dir = f'{WORK_DIR}/{session_label}/{acq.label}'
            os.makedirs(acq_dir, exist_ok=True)

            zip_path = f'{WORK_DIR}/{session_label}/{f.name}'
            acq.download_file(f.name, zip_path)

            # flatten zip into acq_dir OR copy direct dicom
            if f.name.endswith('.zip'):
                with zipfile.ZipFile(zip_path, 'r') as z:
                    for member in z.namelist():
                        filename = os.path.basename(member)
                        if not filename:
                            continue
                        with z.open(member) as src, open(f'{acq_dir}/{filename}', 'wb') as dst:
                            dst.write(src.read())
                os.remove(zip_path)
            else:
                # already a direct dicom file, just move it
                shutil.move(zip_path, f'{acq_dir}/{f.name}')
            
            # create scan and upload
            scan_label = acq.label
            scan = session.scan(scan_label)
            scan.create(**{'xnat:mrScanData/type': scan_label})
            resource = scan.resource('DICOM')
            resource.create()

            dcm_files = [x for x in os.listdir(acq_dir) if x.endswith('.dcm') or x.endswith('.MR')]
            for dcm in dcm_files:
                resource.file(dcm).insert(f'{acq_dir}/{dcm}')

            print(f"  Uploaded {len(dcm_files)} files for {acq.label}")

    # cleanup local files for this session
    shutil.rmtree(f'{WORK_DIR}/{session_label}')
    print(f"  Done — {subject_label} uploaded and cleaned up")

print("\nAll sessions complete.")
