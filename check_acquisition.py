import flywheel
import os
from dotenv import load_dotenv

load_dotenv()

fw = flywheel.Client(os.getenv('FW_API_KEY'))

project = fw.lookup('mrrc/Prisma1QA')
sessions = sorted(project.sessions(), key=lambda s: s.timestamp, reverse=True)

# grab most recent
ses = sessions[0]
print(f"Session: {ses.label} - {ses.timestamp}")

# look at acquisitions
for acq in ses.acquisitions():
    print(f"  Acquisition: {acq.label}")
    for f in acq.files:
        print(f"    File: {f.name} ({f.type})")
