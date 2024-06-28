import threading
import time
import requests
import xml.etree.ElementTree as ET

version_info = {}
version_thread = None
APP_VERSION = "0.9"


def threaded_check():
    while True:
        # TODO: Change with our link :)
        r = requests.get("https://github.com/jellyfin/jellyfin/releases.atom")
        if r.status_code == 200:
            parsed = ET.fromstring(r.text)
            newest = parsed.find("{http://www.w3.org/2005/Atom}entry")

            title = newest.find("{http://www.w3.org/2005/Atom}title").text
            link = newest.find(
                "{http://www.w3.org/2005/Atom}link").attrib['href']
            # updated = newest.find("{http://www.w3.org/2005/Atom}updated").text

            version_info['newest'] = title
            version_info['current'] = '10.9.7'
            # version_info['current'] = APP_VERSION
            version_info['newest_link'] = link
        else:
            # set it to something we can use in admin.html to move it
            print(f"resp is {r.status_code}")
        time.sleep(6*60*60)


def version_check():
    if version_thread is None or not version_thread.is_alive():
        version_thread = threading.Thread(target=threaded_check)
        version_thread.daemon = True
        version_thread.start()
