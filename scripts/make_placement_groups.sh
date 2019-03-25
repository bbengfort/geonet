#!/bin/bash
# aws ec2 delete-placement-group --group-name "alia-partition-pg" --region ap-northeast-1
# aws ec2 delete-placement-group --group-name "alia-partition-pg" --region ap-northeast-2
# aws ec2 delete-placement-group --group-name "alia-partition-pg" --region ap-south-1
# aws ec2 delete-placement-group --group-name "alia-partition-pg" --region ap-southeast-1
# aws ec2 delete-placement-group --group-name "alia-partition-pg" --region ap-southeast-2
# aws ec2 delete-placement-group --group-name "alia-partition-pg" --region ca-central-1
# aws ec2 delete-placement-group --group-name "alia-partition-pg" --region eu-central-1
# aws ec2 delete-placement-group --group-name "alia-partition-pg" --region eu-north-1
# aws ec2 delete-placement-group --group-name "alia-partition-pg" --region eu-west-1
# aws ec2 delete-placement-group --group-name "alia-partition-pg" --region eu-west-2
# aws ec2 delete-placement-group --group-name "alia-partition-pg" --region eu-west-3
# aws ec2 delete-placement-group --group-name "alia-partition-pg" --region sa-east-1
# aws ec2 delete-placement-group --group-name "alia-partition-pg" --region us-east-1
# aws ec2 delete-placement-group --group-name "alia-partition-pg" --region us-east-2
# aws ec2 delete-placement-group --group-name "alia-partition-pg" --region us-west-1
# aws ec2 delete-placement-group --group-name "alia-partition-pg" --region us-west-2

aws ec2 create-placement-group --group-name "alia-partition-pg" --strategy "partition" --partition-count 7 --region ap-northeast-1
aws ec2 create-placement-group --group-name "alia-partition-pg" --strategy "partition" --partition-count 7 --region ap-northeast-2
aws ec2 create-placement-group --group-name "alia-partition-pg" --strategy "partition" --partition-count 7 --region ap-south-1
aws ec2 create-placement-group --group-name "alia-partition-pg" --strategy "partition" --partition-count 7 --region ap-southeast-1
aws ec2 create-placement-group --group-name "alia-partition-pg" --strategy "partition" --partition-count 7 --region ap-southeast-2
aws ec2 create-placement-group --group-name "alia-partition-pg" --strategy "partition" --partition-count 7 --region ca-central-1
aws ec2 create-placement-group --group-name "alia-partition-pg" --strategy "partition" --partition-count 7 --region eu-central-1
aws ec2 create-placement-group --group-name "alia-partition-pg" --strategy "partition" --partition-count 7 --region eu-north-1
aws ec2 create-placement-group --group-name "alia-partition-pg" --strategy "partition" --partition-count 7 --region eu-west-1
aws ec2 create-placement-group --group-name "alia-partition-pg" --strategy "partition" --partition-count 7 --region eu-west-2
aws ec2 create-placement-group --group-name "alia-partition-pg" --strategy "partition" --partition-count 7 --region eu-west-3
aws ec2 create-placement-group --group-name "alia-partition-pg" --strategy "partition" --partition-count 7 --region sa-east-1
aws ec2 create-placement-group --group-name "alia-partition-pg" --strategy "partition" --partition-count 7 --region us-east-1
aws ec2 create-placement-group --group-name "alia-partition-pg" --strategy "partition" --partition-count 7 --region us-east-2
aws ec2 create-placement-group --group-name "alia-partition-pg" --strategy "partition" --partition-count 7 --region us-west-1
aws ec2 create-placement-group --group-name "alia-partition-pg" --strategy "partition" --partition-count 7 --region us-west-2
