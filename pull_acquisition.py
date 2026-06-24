import flywheel
import os
from dotenv import load_dotenv

load_dotenv()

fw = flywheel.Client(os.getenv('FW_API_KEY'))

project = fw.lookup('mrrc/Prisma1QA')
sessions = sorted(project.sessions(), key=lambda s: s.timestamp, reverse=True)

ses = sessions[0]
print(f"Session: {ses.label} - {ses.timestamp}")

for acq in ses.acquisitions():
    print(f"  Acquisition: {acq.label}")
    for f in acq.files:
        print(f"    File: {f.name} ({f.type})")

# download localizer
os.makedirs('test_dicoms', exist_ok=True)

acq = next(a for a in ses.acquisitions() if a.label == 'localizer')

for f in acq.files:
    if f.type == 'dicom':
        print(f"Downloading {f.name}...")
        acq.download_file(f.name, f'test_dicoms/{f.name}')
        print("Done.")
