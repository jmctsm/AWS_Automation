#!python3

"""
Create a vpc in a region with two subnets (1 public and 1 private)
"""

import boto3
import json

region = "us-east-2"
vpc_name = "VPC_A"
cidr_range = "10.10.0.0/16"
public_subnet = "10.10.0.0/24"
private_subnet = "10.10.1.0/24"
public_subnet_name = "Public_Subnet_VPC_A"
private_subnet_name = "Private_Subnet_VPC_A"
internet_gateway_name = "IG_VPC_A"
public_route_table_name = "VPC_A_Public_RT"


def vpc_creation():
    default_region = boto3.setup_default_session(region_name=region)
    ec2 = boto3.resource("ec2")
    # ec2 = boto3.client("ec2")
    ec2Client = boto3.client("ec2")
    vpc = ec2Client.create_vpc(
        CidrBlock=cidr_range,
        TagSpecifications=[
            {
                "ResourceType": "vpc",
                "Tags": [
                    {
                        "Key": "Name",
                        "Value": vpc_name,
                    },
                ],
            },
        ],
    )
    # vpc.wait_until_available()
    vpc_id = vpc["Vpc"]["VpcId"]
    print(f"{vpc_id=}")
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

    # create an internet gateway and attach it to VPC
    # internetgateway = ec2.create_internet_gateway()
    internetgateway = ec2Client.create_internet_gateway(
        TagSpecifications=[
            {
                "ResourceType": "internet-gateway",
                "Tags": [
                    {
                        "Key": "Name",
                        "Value": internet_gateway_name,
                    },
                ],
            },
        ],
    )
    internet_gateway_id = internetgateway["InternetGateway"]["InternetGatewayId"]
    attach_gateway = ec2Client.attach_internet_gateway(
        InternetGatewayId=internet_gateway_id,
        VpcId=vpc_id,
    )
    print(f"{internet_gateway_id=}")

    # create a route table and a public route
    pub_routetable = ec2Client.create_route_table(
        VpcId=vpc_id,
        TagSpecifications=[
            {
                "ResourceType": "route-table",
                "Tags": [
                    {
                        "Key": "Name",
                        "Value": public_route_table_name,
                    },
                ],
            },
        ],
    )
    pub_route_table_id = pub_routetable["RouteTable"]["RouteTableId"]
    route = ec2Client.create_route(
        DestinationCidrBlock="0.0.0.0/0",
        GatewayId=internet_gateway_id,
        RouteTableId=pub_route_table_id,
    )
    print(f"{pub_route_table_id=}")
    # create public subnet and associate it with route table
    public_subnet_obj = ec2Client.create_subnet(
        CidrBlock=public_subnet,
        VpcId=vpc_id,
        TagSpecifications=[
            {
                "ResourceType": "subnet",
                "Tags": [
                    {"Key": "Name", "Value": public_subnet_name},
                ],
            },
        ],
    )
    public_subnet_id = public_subnet_name["Subnet"]["Subnet_Id"]
    public_associate = ec2Client.associate_with_subnet(SubnetId=public_subnet_id)
    print(f"{public_subnet_obj.id=}")

    # create a private route table
    priv_routetable = vpc.create_route_table()
    print(f"{priv_routetable.id=}")

    # create private subnet and associate it with route table
    private_subnet_obj = ec2.create_subnet(
        CidrBlock=private_subnet,
        VpcId=vpc.id,
        TagSpecifications=[
            {
                "ResourceType": "subnet",
                "Tags": [
                    {"Key": "Name", "Value": private_subnet_name},
                ],
            },
        ],
    )
    pub_routetable.associate_with_subnet(SubnetId=private_subnet_obj.id)
    print(f"{private_subnet_obj.id=}")

    output_dict = {
        "default_region": region,
        "vpc_id": vpc_id,
        "internetgateway_id": internet_gateway_id,
        "pub_routetable_id": pub_routetable.id,
        "public_subnet_obj_id": public_subnet_obj.id,
        "priv_routetable_id": priv_routetable.id,
        "private_subnet_obj_id": private_subnet_obj.id,
    }
    json_string = json.dumps(output_dict, indent=4)
    file_name = region + "_" + vpc.id + ".json"
    with open(file_name, "w") as output_file:
        output_file.write(json_string)


if __name__ == "__main__":
    vpc_creation()
