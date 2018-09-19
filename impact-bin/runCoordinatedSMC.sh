#!/bin/bash

# Step 1: Walk this way. 
if [ "$#" -ne 2 ]; then
    echo "usage: runSMC.sh numberToBeSummed partyNumber" > /dev/stderr
    exit
fi

cd /home/ec2-user/SPDZ-2

rm -f /tmp/resultTotal /tmp/smcerr /tmp/se /tmp/so

echo $1 | /home/ec2-user/SPDZ-2/Player-Online.x -h 172.31.21.194 -pn 5000 $2 tripleadd 2>/tmp/se > /tmp/so

mv /tmp/se /tmp/smcerr
mv /tmp/so /tmp/resultTotal
