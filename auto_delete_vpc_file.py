#!python3

"""
Create a vpc in a region with two subnets (1 public and 1 private)
"""

import boto3
import argparse
import json
import os


def vpc_deletion(input_dict):
    region = input_dict["region"]
    vpc_id = input_dict["vpc_id"]
    internetgateway_id = input_dict["internet_gateway_id"]
    route_info_list = input_dict["route_info"]
    default_region = boto3.setup_default_session(
        region_name=region,
    )
    client = boto3.client("ec2")

    # detach internet gateway
    response = client.detach_internet_gateway(
        InternetGatewayId=internetgateway_id,
        VpcId=vpc_id,
    )
    print(f"{response['ResponseMetadata']['HTTPStatusCode']}")
    # delete internet gateway
    if internetgateway_id is not False:
        response = client.delete_internet_gateway(
            InternetGatewayId=internetgateway_id,
        )
        print(f"{response['ResponseMetadata']['HTTPStatusCode']}")

    # delete subnets and route tables
    for route_info in route_info_list:
        response = client.delete_subnet(
            SubnetId=route_info[1],
        )
        print(f"{response['ResponseMetadata']['HTTPStatusCode']}")

        response = client.delete_route_table(
            RouteTableId=route_info[0],
        )
        print(f"{response['ResponseMetadata']['HTTPStatusCode']}")

    # delete vpc
    response = client.delete_vpc(
        VpcId=vpc_id,
    )
    print(f"{response['ResponseMetadata']['HTTPStatusCode']}")


def parse_args():
    """
    parse the arguments and pass them back to main
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-j",
        "--json",
        type=str,
        required=True,
        help="JSON file to parse",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    with open(args.json, "r") as json_file:
        data = json.load(json_file)
    vpc_deletion(data)

    # delete input file
    os.remove(args.json)
