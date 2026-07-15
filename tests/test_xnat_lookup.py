import dotenv
import os
import requests
import pytest
from redcap_xnat import find_xnat

@pytest.mark.skipif(os.path.isfile(".venv"), reason="missing .env for credentials")
def test_find_xnat_url():
    dotenv.load_dotenv()
    xnat = requests.Session()
    xnat.auth = (os.getenv("XNAT_USER"), os.getenv("XNAT_PASS"))
    find_xnat(xnat, xnat_url = os.getenv("XNAT_EXAMPLE_URL"))
    pass
