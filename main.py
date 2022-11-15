import requests
import json
import os
import boto3
from botocore.exceptions import ClientError
import ipaddress

def get_prefix_list_id(list_name):
    client = boto3.client("ec2", region_name="us-west-2")
    response = client.describe_managed_prefix_lists(
        MaxResults=100,
        Filters=[
            {
                "Name": "prefix-list-name",
                "Values": [list_name]
            }
        ]
    )
    for p_list in response['PrefixLists']:
        return {"ID": p_list['PrefixListId'], "VERSION": p_list['Version']}

def update_managed_prefix_list(list_name, ip):
    client = boto3.client("ec2", region_name="us-west-2")
    try:
        response = client.modify_managed_prefix_list(
                    DryRun=False,
                    PrefixListId=get_prefix_list_id(list_name)['ID'],
                    CurrentVersion=get_prefix_list_id(list_name)['VERSION'],
                    AddEntries=[
                        {
                            "Cidr": ip
                        }
                    ]
                )
        return True
    except ClientError as e:
        print(e)
        print("Failed to update list")
def check_ip_type(list_name, ip_list):
    for ip in ip_list:
        if type(ipaddress.ip_address(ip[:-3])) is ipaddress.IPv6Address:
            managed_prefix_list_name = "git-" + list_name + "-ipv6"
            print(ip)
            update_managed_prefix_list(managed_prefix_list_name, ip)
        else:
            managed_prefix_list_name = "git-" + list_name + "-ipv4"
            print(ip)
    pass

if __name__ == "__main__":
    url = "https://api.github.com/meta"
    headers = {"Accept": "application/vnd.github+json", "Authorization": "Bearer "+ os.environ['SECRET']}
    r = requests.get(url, headers=headers)
    json_ips = json.loads(r.content)
    hooks = json_ips['hooks']

    check_ip_type("hooks", hooks)
