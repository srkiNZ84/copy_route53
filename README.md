# Copy Route53

## About

Python script to copy DNS resource records (also known as "entries") from one AWS account to another.

## Dependencies

* Python3
* boto3 pip package

## How to run

From the shell:
```
  ./copy_records.py [AWS SRC PROFILE] [AWS DEST PROFILE] [ROUTE53 SRC ZONEID] [ROUTE53 DEST ZONEID]
```
e.g.
```
  ./copy_records.py prod-us-east dev-aus Z88BLCEHEPMCULZ Z9H86HBLC614T
```
