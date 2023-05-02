"""ifps file handle"""
import io
import base64
import requests

MASK_URL = "https://mask.infura-ipfs.io/ipfs/"
IFPS_URL = "https://ipfs.io/ipfs/"


def add_file(file):
    """add ifps file"""
    url = "https://ipfs.infura.io:5001/api/v0/add"
    files = {"file": io.BytesIO(file)}
    auth = base64.b64encode(
        b"<api_key>"
    )
    response = requests.post(
        url,
        files=files,
        headers={"authorization": f"Basic {auth.decode()}"},
        timeout=3,
    )
    file_hash = response.json()["Hash"]
    return IFPS_URL + file_hash
