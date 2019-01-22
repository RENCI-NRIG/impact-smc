#!/bin/bash

# Step 1: Walk this way. 
if [ "$#" -ne 1 ]; then
    echo "usage: runICEES.sh study-name" > /dev/stderr
    exit
fi

curl --silent -k -XPOST https://icees.renci.org/1.0.0/patient/2010/cohort -H "Content-Type: application/json" -d '{"AvgDailyPM2.5Exposure":{"operator":">", "value":1}}' | python -m json.tool 2>/tmp/ICEerrorBaby > /tmp/ICEout

mv /tmp/ICEerrorBaby /tmp/ICEESstderr
mv /tmp/ICEout /tmp/ICEESstdout
