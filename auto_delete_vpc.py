#!python3

"""
Create a vpc in a region with two subnets (1 public and 1 private)
"""

import boto3

region = "us-east-2"
vpc_name = "VPC_A"
cidr_range = "10.10.0.0/16"
public_subnet = "10.10.0.0/24"
private_subnet = "10.10.1.0/24"
public_subnet_name = "Public_Subnet_VPC_A"
private_subnet_name = "Private_Subnet_VPC_A"
vpc_id = "vpc-04a0be9860710c6b3"
internetgateway_id = "igw-07763038b19dd75b0"
pub_routetable_id = "rtb-0e33b010a90285bb2"
pub_subnet_id = "subnet-0d875d84ca5c998e0"
priv_routetable_id = "rtb-0b57bee17c6ae0b68"
priv_subnet_id = "subnet-0e74790a2e7338efa"


def vpc_deletion():
    default_region = boto3.setup_default_session(
        region_name=region,
    )
    ec2 = boto3.resource("ec2")
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


if __name__ == "__main__":
    vpc_deletion()
