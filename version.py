import threading
import time
import requests
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError
from requests.exceptions import ConnectionError

version_info = {}
version_thread = None
# TODO: Change with our link && change the version to the right date (not just Jellyfin copied stuff) :)
ATOM_LINK = "https://github.com/jellyfin/jellyfin/releases.atom"
APP_VERSION = "10.9.6"


def update_version_info():
    # print(time.time())
    version_info['current'] = APP_VERSION
    version_info['newest_link'] = None
    version_info['newest'] = None

    try:
        r = requests.get(ATOM_LINK)
        if r.status_code == 200:
            parsed = ET.fromstring(r.text)
            newest = parsed.find("{http://www.w3.org/2005/Atom}entry")
            if newest is not None:
                title = newest.find("{http://www.w3.org/2005/Atom}title").text
                version_info['newest'] = title

                link = newest.find(
                    "{http://www.w3.org/2005/Atom}link").attrib.get('href', None)
                version_info['newest_link'] = link

    # Parse Error when malformed XML, AttributeError when XML is goofed, ConnectionError when no internet
    except (ParseError, AttributeError, ConnectionError):
        pass

        # print(f"resp is {r.status_code}")


def threaded_check():
    while True:
        update_version_info()
        time.sleep(6*60*60)


def version_check():
    global version_thread
    if version_thread is None or not version_thread.is_alive():
        version_thread = threading.Thread(target=threaded_check)
        version_thread.daemon = True
        version_thread.start()
