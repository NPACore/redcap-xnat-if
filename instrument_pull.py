#!/use/bin/env python
import redcap
import os
from dotenv import load_dotenv
import json

load_dotenv()

URL = os.getenv('REDCAP_URL')
TOKEN = os.getenv('REDCAP_TOKEN')

project = redcap.Project(URL, TOKEN)

# Pull field names
fields = project.field_names
print('Fields:', fields)

# Pull all records
records = project.export_records()
print(json.dumps(records, indent=2))
