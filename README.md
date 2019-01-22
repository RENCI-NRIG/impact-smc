# impact-smc
SMC-related code, configuration files and docs


THINGS TO KNOW...
---

1) export LD_LIBRARY_PATH=/usr/local/lib   # may not need now after ldconfig
2) export TERM=xterm-256color   # needed for zenburn theme - avoid eye pain.
3) edit ~/me - make it my amazon internal reachable IP addr - 172.X.X.X
4) edit ~/others - list other party IP addresses
5) edit ~/port - port number to run on. 5008 works well.
5) edit ~/parties - this contains All o the Parties!!!  (No colons, no ports)
6) edit the ~/pushem script to have the right IP addresses. TODO - make this
   use "others", and fix wherever other is read elsewhere to do something smart
   about the colons.
7) edit ~/ICEES , put "True" in there if this node should use ICEES query
8) source activate impact
9) export FLASK_APP=flaskr     # already done for you in .bashrc
10) flask run --host=0.0.0.0 --port=5008

