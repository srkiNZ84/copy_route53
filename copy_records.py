#!/Library/Frameworks/Python.framework/Versions/3.6/bin/python3

import json
import subprocess
import boto3
import argparse

parser = argparse.ArgumentParser(description='Copy the DNS \
        resource records from one AWS account and domain \
        to another.')
parser.add_argument('srcProfile', type=str, \
        help='AWS profile to use for the SRC account/domain')
parser.add_argument('destProfile', type=str, \
        help='AWS profile to use for the DEST account/domain')
parser.add_argument('srcZoneid', type=str, \
        help='Route53 ZoneId to use for the SRC of the copy')
parser.add_argument('destZoneid', type=str, \
        help='Route53 ZoneId to use for the DEST of the copy')
args = parser.parse_args()

fromProfile = args.srcProfile
toProfile = args.destProfile
fromZoneId=args.srcZoneid
toZoneId=args.destZoneid

print("Copying DNS records from %s/%s to %s/%s" % \
        (fromProfile,fromZoneId,toProfile,toZoneId))

fromSession = boto3.Session(profile_name=fromProfile)
fromRoute53Client = fromSession.client('route53')

toSession = boto3.Session(profile_name=toProfile)
toRoute53Client = toSession.client('route53')

rrsToCopy = fromRoute53Client.list_resource_record_sets(\
#    StartRecordName='www.example.com',
    HostedZoneId=fromZoneId)

# TODO: Modify the code to handle pagination automatically
if rrsToCopy['IsTruncated']:
    print('Record list truncated!')
    print("Next record to get is: ", rrsToCopy['NextRecordName'])

for resourceRecordSet in rrsToCopy['ResourceRecordSets']:
    if resourceRecordSet['Type'] == 'NS' or resourceRecordSet['Type'] == 'SOA':
        continue

    keyname = 'ResourceRecords'
    recordsOrAliasTarget = resourceRecordSet.get('ResourceRecords',[])
    if recordsOrAliasTarget == []:
        keyname = 'AliasTarget'
        recordsOrAliasTarget = resourceRecordSet.get('AliasTarget',[])

    print("\n\nName:\t", resourceRecordSet['Name'], \
            "Type:\t", resourceRecordSet['Type'], \
            "Value:\t", recordsOrAliasTarget, \
            "TTL:\t", resourceRecordSet.get('TTL', 'null'), \
            "RR:\t", keyname)

    ourChangeBatch={
        "Changes": [
            {
                "Action": "UPSERT",
                "ResourceRecordSet": {
                    "Name": resourceRecordSet["Name"],
                    "Type": resourceRecordSet["Type"],
                    keyname: recordsOrAliasTarget
                }
            }
        ]
    }

    print("Changeset: ", ourChangeBatch)

    if "TTL" in resourceRecordSet.keys():
        ourChangeBatch["Changes"][0]["ResourceRecordSet"]["TTL"] = resourceRecordSet["TTL"]

    try:
        updateResponse = toRoute53Client.change_resource_record_sets(\
            HostedZoneId=toZoneId,
            ChangeBatch=ourChangeBatch)
    except Exception as ex:
        print("Update went wrong: ", type(ex), " details: ", ex)

