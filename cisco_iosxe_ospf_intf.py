#!/usr/bin/env python3

from requests.exceptions import JSONDecodeError
import yaml
import requests
import json


def get_ospf(host, username, password):
    
    # The IOS-XE sandbox uses a self-signed cert at present, so let's
    # ignore any obvious security warnings for now.
    requests.packages.urllib3.disable_warnings()

    # The API path below is what the DevNet sandbox uses for API testing,
    # which may change in the future. Be sure to check the IP address as
    # I suspect this changes frequently. See here for more details:
    # https://developer.cisco.com/site/ios-xe

    # Create 2-tuple for "basic" authentication using Cisco DevNet credentials.
    # No fancy tokens needed to get basic RESTCONF working on Cisco IOS-XE.
    auth = (username, password)

    # Define headers for issuing HTTP GET requests to receive YANG data as JSON.
    headers = {"Accept": "application/yang-data+json", 'Content-Type': 'application/yang-data+json'}

    # Issue a GET request to collect the OSPF process only. This will
    # return a list of dictionaries where each dictionary represents a route.
    # The URL is broken over multiple lines for readability, and the "=" is
    # used to specify specific "keys" to query individual list elements.
    api = f"https://{host}/restconf/data/"
    get_intf_path = "native/interface/"
    get_hostname_path = "Cisco-IOS-XE-native:native/hostname/"
    get_intf_status = requests.get(
        api + get_intf_path,
        headers=headers,
        auth=auth,
        verify=False,
    )
    get_hostname_config = requests.get(
        api + get_hostname_path,
        headers=headers,
        auth=auth,
        verify=False,
    )

    # Uncomment the line below to see the JSON response; great for learning
    # import json; print(json.dumps(get_intf_status.json(), indent=2))

    # Print route details in a human-readable format
    # print(get_intf_status.status_code)
    Hostname = get_hostname_config.json()["Cisco-IOS-XE-native:hostname"]
    print(f"Checking Device {Hostname}")
    intfs = get_intf_status.json()["Cisco-IOS-XE-native:interface"]
    for k, v in intfs.items():
        for intf in v:
            try:
                if "Cisco-IOS-XE-ospf:router-ospf" in intf["ip"]:
                    print(k, intf["name"])
                    print(intf)
            except KeyError:
                print("")
def main():
    with open("device_info.yml", "r") as handle:
        device_info = yaml.safe_load(handle)
        for router in device_info["ios-xe"]:
            get_ospf(router["mgmt_ip"], router["username"], router["password"])

if __name__ == "__main__":
    main()
