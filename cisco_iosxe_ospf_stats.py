#!/usr/bin/env python3

from requests.exceptions import JSONDecodeError
import yaml
import requests
import json


def get_ospf(host, username, password):
    """
    Execution begins here.
    """

    # The IOS-XE sandbox uses a self-signed cert at present, so let's
    # ignore any obvious security warnings for now.
    requests.packages.urllib3.disable_warnings()

    # Create 2-tuple for "basic" authentication using Cisco DevNet credentials.
    # No fancy tokens needed to get basic RESTCONF working on Cisco IOS-XE.
    auth = (username, password)

    # Define headers for issuing HTTP GET requests to receive YANG data as JSON.
    headers = {"Accept": "application/yang-data+json", 'Content-Type': 'application/yang-data+json'}

    # Issue a GET request to collect the OSPF process only. This will
    # return a list of dictionaries where each dictionary represents a route.
    # The URL is broken over multiple lines for readability, and the "=" is
    # used to specify specific "keys" to query individual list elements.
    try:
        api = f"https://{host}/restconf/data/"
        get_ospf_path = "Cisco-IOS-XE-ospf-oper:ospf-oper-data/ospf-state/ospf-instance/"
        get_hostname_path = "Cisco-IOS-XE-native:native/hostname/"
        get_ospf_stats = requests.get(
            api + get_ospf_path,
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
        # import json; print(json.dumps(get_ospf_stats.json(), indent=2))

        # Print route details in a human-readable format
        # print(get_ospf_stats.status_code)
        Hostname = get_hostname_config.json()["Cisco-IOS-XE-native:hostname"]
        print(f"Checking Device {Hostname}")
        PID = get_ospf_stats.json()["Cisco-IOS-XE-ospf-oper:ospf-instance"][0]
        print(f"OSPF Process ID: {PID['process-id']}\n\n", end="")
    except JSONDecodeError:
        if get_ospf_stats.status_code == 204:
            print("No OSPF Process configured yet, Create OSPF Process")
            get_Lo0_ipaddr_path = "Cisco-IOS-XE-native:native/interface/Loopback=0/ip/address/primary/address"
            Lo0_ipaddr = requests.get(
                api + get_Lo0_ipaddr_path,
                headers=headers,
                auth=auth,
                verify=False,
            ).json()["Cisco-IOS-XE-native:address"]
            # print(Lo0_ipaddr)
            payload = json.dumps({
                "ospf": [
                    {
                    "id": 10,
                    "router-id": Lo0_ipaddr
                    }
                ]
            })
            # print(payload)
            patch_ospf_path = "Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-ospf:ospf"
            create_ospf_process = requests.patch(
                api + patch_ospf_path,
                headers=headers,
                auth=auth,
                data=payload,
                verify=False,
                )
            get_ospf_stats = requests.get(
                api + get_ospf_path,
                headers=headers,
                auth=auth,
                verify=False,
            )
            print("Validating OSPF Process again")
            PID = get_ospf_stats.json()["Cisco-IOS-XE-ospf-oper:ospf-instance"][0]
            print(f"OSPF Process ID: {PID['process-id']}\n\n", end="")

def main():
    with open("device_info.yml", "r") as handle:
        device_info = yaml.safe_load(handle)
        for router in device_info["ios-xe"]:
            get_ospf(router["mgmt_ip"], router["username"], router["password"])

if __name__ == "__main__":
    main()
