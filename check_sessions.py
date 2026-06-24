import flywheel
import os
from dotenv import load_dotenv

load_dotenv()

fw = flywheel.Client(os.getenv('FW_API_KEY'))

project = fw.lookup('mrrc/Prisma1QA')
print(f"Project: {project.label}")

sessions = project.sessions()
for ses in sessions:
    print(f" {ses.label} - {ses.timestamp}")
