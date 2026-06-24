import pyxnat
import os
from dotenv import load_dotenv

load_dotenv()

xnat = pyxnat.Interface(
        server='http://10.48.86.97',
        user=os.getenv('XNAT_USER'),
        password=os.getenv('XNAT_PASS')
)

print(xnat.head('/data/JSESSION'))

project = xnat.select.project('Test_Project')
project.create()

projects = xnat.select.projects().get()
print(projects)
