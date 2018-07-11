import argparse 
import re
import requests
import csv
import lxml.html
import time
from netaddr import IPRange



#Parsing CLI Input
parser = argparse.ArgumentParser()
parser.add_argument('startip', type=str, help='Start IP Address')
parser.add_argument('endip', type=str, nargs='?', default=None, help='End IP Address')

args = parser.parse_args()
if args.endip == None:
    args.endip = args.startip

iprange = IPRange(args.startip, args.endip)



#Initializing Variable
ip_phone = 0
start_time = time.time()


#Parsing Inventory of IPPhone
def scrape(r):
    # Parse html table into a list using xpath expressions
    doc = lxml.html.fromstring(r.text)
    stuff = (doc.xpath('.//b/text()'))

    # Use dict comprehension to convert list into dict
    d = dict([(k.strip(), v) for k, v in zip(stuff[::2], stuff[1::2])])

    # Gather the dict values into variables
    mac = (d.get('MAC Address'))
    hname = (d.get('Host Name'))
    serial = (d.get('Serial Number'))
    modelnum = (d.get('Model Number'))
    appload = (d.get('App Load ID'))
    bootload = (d.get('Boot Load ID'))
    hdware = (d.get('Hardware Revision'))

    # Write data to csv file
    with open('IP_Phones.csv', 'a', newline='') as f:
        more_data = [ip, serial, mac, hname, modelnum, appload, bootload, hdware]
        writer = csv.writer(f)
        writer.writerow(more_data)

    # Printing to Console
    print('{0:20}{1:20}{2:20}'.format(str(ip), '[Found]', serial))



#Printing Output Title
print('From: ' + args.startip)
print('To: ' + args.endip)
print('---------------')


#Checking IPPhone Web Interface Status
for ip in iprange:
    try:
        r = requests.get('http://' + str(ip), timeout=0.5)

        # If the response is OK,
        # then search for 'IP phone' via regular expressions
        if r.status_code == 200:
            verify_cisco = re.compile(r'(ip phone)', re.I)
            mo = verify_cisco.search(r.text)

            if mo is not None:
                ip_phone += 1
                scrape(r)

    except Exception as err:
        'There was an error'


#Printing Summary Info

print('---------------')
scan_time = round(time.time() - start_time)
print('The scan took', scan_time, 'seconds to run.')
print('Find ', ip_phone, 'IP phones.')

