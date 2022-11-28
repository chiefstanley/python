#!/usr/bin/env python3

import requests
import psycopg2
import csv
from jinja2 import Template


with open("source_interface.csv") as srcint:
    reader = csv.DictReader(srcint)
    with open("juniper_xml_post_RequestBody.j2") as t:
        intf_temp = Template(t.read())
        for row in reader:
            interface_xml_config = intf_temp.render(
                interface = row["interface"],
                unit = row["unit"],
                IP = row["IP"]
            )
            url = ("http://{}:8080/rpc?stop-on-error=1").format(row["router"])
            headers = {
                'Accept': 'application/xml',
                'Content-Type': 'application/xml',
                'Authorization': 'Basic cm9vdDpKdW5pcGVy'
            }
            response = requests.request("POST", url, headers=headers, data=interface_xml_config)

            print(response.text)
