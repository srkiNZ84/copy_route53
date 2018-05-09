#!/bin/bash

FROM_PROFILE=firstaccount
TO_PROFILE=secondaccount

for ZONE in `aws --profile $FROM_PROFILE route53 list-hosted-zones | jq -r '.HostedZones[].Name'`
do
  CALLER_REFERENCE=`date +%s`
  echo "Copying $ZONE from $FROM_PROFILE AWS profile account to $TO_PROFILE AWS profile account with caller reference $CALLER_REFERENCE"
  aws --profile $TO_PROFILE route53 create-hosted-zone --name $ZONE --caller-reference $CALLER_REFERENCE
done


