#!/bin/bash

# make sure we aren't already running a party or a server, kill it if 
# we are, and start another server.  Server is only used for mutual
# player discovery and connection handoff, and no secret data 
# flows through it.

cd /home/ec2-user/SPDZ-2
export LD_LIBRARY_PATH=/usr/local/lib
/bin/kill Player-Online.x
/bin/kill Server.x
nohup ./Server.x 3 5000 >& /tmp/srv$$ &

sleep 20   # for debugging time.
