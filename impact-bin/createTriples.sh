#!/bin/bash

cd /home/ec2-user/SPDZ-2/

#./spdz2-offline.x -p 0 -N 3 -h `cat /home/escott/me | head -1`  -c 3 &
sleep 600
/bin/kill spdz2-offline.x
sleep 90

#./spdz2-offline.x -p 1 -N 3 -h `cat /home/escott/me | head -1`  -c 3 &
sleep 600
/bin/kill spdz2-offline.x
sleep 90

#./spdz2-offline.x -p 2 -N 3 -h `cat /home/escott/me | head -1`  -c 3 &
sleep 600
/bin/kill spdz2-offline.x
sleep 90

