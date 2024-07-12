#!python3

"""
Create a vpc in a region with two subnets (1 public and 1 private)
"""

import boto3
import argparse
import json
import os


def vpc_deletion(input_dict):

    region = input_dict["default_region"]
    vpc_id = input_dict["vpc_id"]
    internetgateway_id = input_dict["internetgateway_id"]
    pub_routetable_id = input_dict["pub_routetable_id"]
    pub_subnet_id = input_dict["public_subnet_obj_id"]
    priv_routetable_id = input_dict["priv_routetable_id"]
    priv_subnet_id = input_dict["private_subnet_obj_id"]

    default_region = boto3.setup_default_session(
        region_name=region,
    )
    client = boto3.client("ec2")
    # delete private subnet
    response = client.delete_subnet(
        SubnetId=priv_subnet_id,
    )
    print(f"{response=}")

    # delete private route table
    response = client.delete_route_table(
        RouteTableId=priv_routetable_id,
    )
    print(f"{response=}")

    # detach internet gateway
    response = client.detach_internet_gateway(
        InternetGatewayId=internetgateway_id,
        VpcId=vpc_id,
    )
    # delete internet gateway
    response = client.delete_internet_gateway(
        InternetGatewayId=internetgateway_id,
    )
    print(f"{response=}")

    # delete public subnet
    response = client.delete_subnet(
        SubnetId=pub_subnet_id,
    )
    print(f"{response=}")

    # delete public route table
    response = client.delete_route_table(
        RouteTableId=pub_routetable_id,
    )
    print(f"{response=}")

    # delete vpc
    response = client.delete_vpc(
        VpcId=vpc_id,
    )
    print(f"{response=}")


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
