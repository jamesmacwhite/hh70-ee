#!/usr/bin/env python
"""
<Program Name>
    say_lte.py

<Authors>
    Lukas Puehringer <luk.puehringer@gmail.com>
    James White <james@jmwhite.co.uk>

<Purpose>
    Script to help position various Alcatel routers that use a JSON-RPC API

    If a change in signal strength is detected, it uses the macOS command line
    tool `say` to say the new signal strength.

<Usage>
    1. Connect your computer to your Alcatel WiFi
    2. Open a browser and go to the admin page e.g. `192.168.1.1`
    3. Open your browser's developer tools, go to the `network` tab and look
       for requests to `http://192.168.1.1/jrd/webapi`
    4. Take any request, copy the value of the header
      `_TclRequestVerificationKey` and note it down.
    5. Turn up the volume of your computer and run the script
    6. Walk your Alcatel router around your apartment (long extension cord is
       helpful) and place it at where your computer tells you a high signal.

"""

import time
import requests
import subprocess
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('requestKey', help='_TclRequestVerificationKey header')
parser.add_argument('routerIPAddress', help='The LAN IP of your router', nargs='?', default='192.168.1.1')
parser.add_argument('jrdId', help='ID value used with JSON-RPC API calls', nargs='?', type=int, default=1)
args = parser.parse_args()

URL = 'http://' + args.routerIPAddress + '/jrd/webapi'

# JSON rpc request to get information such as signal strength
JSON_REQUEST = {
  "id": str(args.jrdId),
  "jsonrpc": "2.0",
  "method": "GetSystemStatus",
  "params": {}
}

# Headers required to authenticate with JSON rpc (assessed by trial and error)
HEADERS = {
  "_TclRequestVerificationKey": args.requestKey,
  "Referer": "http://" + args.routerIPAddress + "/index.html"
}

def main():
  """ Run indefinitely to (at an interval of 1 second)
    - print requested signal strength to command line, and
    - if signal strength changes, `say` the new strength.
  """
  last = None
  while True:
    r = requests.post(URL, json=JSON_REQUEST, headers=HEADERS)
    strength = r.json().get("result", {}).get("SignalStrength")

    print "Signal Strength:", strength
    if strength != last:
      process = subprocess.Popen(["say", 'Signal strength is now ' + str(strength)],
          stdout=subprocess.PIPE)
      process.communicate()

    last = strength
    time.sleep(1)

if __name__ == "__main__":
  main()
