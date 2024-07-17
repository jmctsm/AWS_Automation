#!python3

"""
Create a vpc in a region with two subnets (1 public and 1 private)
"""

import boto3
import json
import yaml
import argparse


def vpc_creation(
    input_dict,
):
    for network in input_dict["networks"]:
        boto3.setup_default_session(region_name=network["region"])
        ec2Client = boto3.client("ec2")
        for vpc_to_create in network["vpcs"]:
            vpc = ec2Client.create_vpc(
                CidrBlock=vpc_to_create["cidr_range"],
                TagSpecifications=[
                    {
                        "ResourceType": "vpc",
                        "Tags": [
                            {
                                "Key": "Name",
                                "Value": vpc_to_create["name"],
                            },
                        ],
                    },
                ],
            )
            vpc_id = vpc["Vpc"]["VpcId"]
            # enable public dns hostname so that we can SSH into it later
            ec2Client.modify_vpc_attribute(
                VpcId=vpc_id,
                EnableDnsSupport={
                    "Value": True,
                },
            )
            ec2Client.modify_vpc_attribute(
                VpcId=vpc_id,
                EnableDnsHostnames={
                    "Value": True,
                },
            )
            print(f"{vpc_id=}")
            if vpc_to_create["internet_gateway_name"]:
                # create an internet gateway and attach it to VPC
                internetgateway = ec2Client.create_internet_gateway(
                    TagSpecifications=[
                        {
                            "ResourceType": "internet-gateway",
                            "Tags": [
                                {
                                    "Key": "Name",
                                    "Value": vpc_to_create["internet_gateway_name"],
                                },
                            ],
                        },
                    ],
                )
                internet_gateway_id = internetgateway["InternetGateway"][
                    "InternetGatewayId"
                ]
                # internetgateway = ec2.create_internet_gateway()
                attach_gateway = ec2Client.attach_internet_gateway(
                    InternetGatewayId=internet_gateway_id,
                    VpcId=vpc_id,
                )
            else:
                internet_gateway_id = False
            print(f"{internet_gateway_id=}")

            # create route tables
            route_table_list = []
            for route_info in vpc_to_create["routing"]:
                created_route_table = ec2Client.create_route_table(
                    VpcId=vpc_id,
                    TagSpecifications=[
                        {
                            "ResourceType": "route-table",
                            "Tags": [
                                {
                                    "Key": "Name",
                                    "Value": route_info["route_table_name"],
                                },
                            ],
                        },
                    ],
                )
                route_table_id = created_route_table["RouteTable"]["RouteTableId"]
                if route_info["default_route"]:
                    route = ec2Client.create_route(
                        DestinationCidrBlock="0.0.0.0/0",
                        GatewayId=internet_gateway_id,
                        RouteTableId=route_table_id,
                    )
                ec2Resource = boto3.resource("ec2")

                subnet_obj = ec2Resource.create_subnet(
                    CidrBlock=route_info["subnet_cidr"],
                    VpcId=vpc_id,
                    AvailabilityZone=route_info["availability_zone_id"],
                    TagSpecifications=[
                        {
                            "ResourceType": "subnet",
                            "Tags": [
                                {
                                    "Key": "Name",
                                    "Value": route_info["subnet_name"],
                                },
                            ],
                        },
                    ],
                )
                # Associate with route table
                # subnet_associate = ec2Resource.RouteTableAssociation(route_table_id)
                subnet_associate = ec2Client.associate_route_table(
                 RouteTableId=route_table_id,
                 SubnetId=subnet_obj.id,
                )
                # print(f"{subnet_id=}")
                print(f"{subnet_obj.id=}")
                print(f"{route_table_id=}")
                route_table_list.append((route_table_id, subnet_obj.id))
            output_dict = {
                "region": network["region"],
                "vpc_id": vpc_id,
                "internet_gateway_id": internet_gateway_id,
                "route_info": route_table_list,
            }
            print(output_dict)
            json_string = json.dumps(output_dict, indent=4)
            file_name = f"{network['region']}_{vpc_to_create["name"]}_{vpc_id}.json"
            with open(file_name, "w") as output_file:
                output_file.write(json_string)


def parse_args():
    """
    parse the arguments and pass them back to main
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-y",
        "--yaml_input",
        type=str,
        required=True,
        help="YAML file to parse for configurations",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    with open(args.yaml_input, "r") as input_file:
        input_dict = yaml.load(input_file, Loader=yaml.SafeLoader)
    vpc_creation(input_dict)
