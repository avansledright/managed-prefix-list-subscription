import requests
import json
import os
import boto3
from botocore.exceptions import ClientError
import ipaddress

def check_for_existing(list_id, ip):
    client = boto3.client("ec2", region_name="us-west-2")
    try:
        response = client.get_managed_prefix_list_entries(
            PrefixListId=list_id,
            MaxResults=100,
        )
        for entry in response['Entries']:
            if entry['Cidr'] == ip:
                return True
            else:
                pass
        return False
    except ClientError as e:
        print(e)



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
    if check_for_existing(get_prefix_list_id(list_name)['ID'], ip) == True:
        print("Rule already exists")
        return False
    else:
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

if __name__ == "__main__":
    url = "https://<my IP address URL>"
    headers = {}
    r = requests.get(url, headers=headers)
    json_ips = json.loads(r.content)
    ip = ""
    list_name = ""
    result = update_managed_prefix_list(list_name, ip)
    if result == True:
        print("Successfully Updates lists")
    else:
        print("Failed to update lists")