# impact-smc
SMC-related code, configuration files and docs

## How ImPACT Implements Secure Multiparty Computation using SPDZ/2

### An overview and walkthrough of Renci’s application of SMC/MPC
    methods for use in the Social Sciences and beyond.

ImPACT SMC provides a simplified way for researchers to collaborate
without having to share their data. It allows groups to compute a
function, known to each of them, using input values that are only
known by their owners. This makes group research much more feasible
across institutional boundaries. The ImPACT SMC implementation is
currently focussed on “cohort discovery”. This task is, simply stated,
dtermining if there are enough potential study participants who meet a
specific set of criteria. The project is, of course, broadly applicable
to any problem domain.

An example of our motivating use case comes from healthcare. Let’s
assume there are three researchers at three institutions. They’re
trying to determine if they have enough patients to form an
experimental cohort, but only certain patients would qualify. For
instance, they might want to know how many patients smoke, live near a
highway, and take a blood pressure medication. They cannot reveal
their individual number of potential cohort members and if that number
is less than ten then they have to report zero to help prevent
“re-identification”. SMC allows the researchers in this case to
determine the total number of possible participants (to decide if
there would potentially be a large enough group to do a meaningful
study with) while not revealing their local, private number. SMC also
can lead to a lower cutoff number for re-identification.

Importantly, ImPACT SMC does not on its own determine the number of
potential cohort members. It is up to the individual researchers at
each institution to compute that number. It is necessary for the users
to agree, ahead of time, on what combination of parameters to screen
for. This coordination is needed because each institution’s database
schema will be different and the queries will have to be custom for
each site. The participants must agree on a identifier for the
potential cohort, as well. They might come to the agreement “Let’s see
how many people smoke, live in an area with a lot of pollution, and
are 20 or more pounds overweight. In addition, we’ll call this
possible cohort “AliceSmithExperiment31”. Note that ImPACT SMC also
has REST-based access to ICEES, part of the NIH-funded Data Translator
project. ICEES implements a common query method across different sites
and the interface makes it possible to skip all of the coordination
beforehand and simply launch queries automatically.

Architecturally, ImPACT SMC consists of a user-facing page on a web
server, a REST interface for coordinating activities, and a database
interface for querying individual results. As an additional
demonstration, a REST interface has been created to facilitate using a
new NIH-sponsored protocol for exchanging some kinds of protected
healthcare data. This document will describe how the Bristol SPDZ/2
SMC/MPC package is used and how each of the components we’ve developed
interface to that package and simplify using it. The initial section,
though, is a description of how to install and use it.


Installation from Virtual Machine Images

There are two ways to install the ImPACT SMC component – either
install it from the github repositories or install a virtual machine
image. Of the two, installing the image is by far the easier one.

To install the package from a VM image, log into your Amazon AWS
account and create a new instance. A “t2.micro” instance is enough for
day-to-day use (and is in the “free tier” if that’s an option for
you), but if you need to generate new keys then you’ll need an
instance with 4 megs of RAM or more. A “t3.medium” instance with two
threads and four megs is completely adequate.

When you’re creating an instance, you’ll have to specify what
operating system image to install. Select the “renciSPDZt2V08” image
(“08” is the current highest version number in January of 2019, but
select the latest version you can find). This image is based on
“Amazon Linux”, which is the default and rather compact
installation. For network security, allow incoming connections on
ports 4999-5008 or specify “SPDZsecurityGroup”. Once the image starts,
log in to it as normal. The only username provided is “ec2-user”, just
like regular Amazon Linux, and the account is a sudoer. Keep in mind
that to be useful, or even functional, you’ll need at least three
instances. You don’t have to “own” all of them (after all, that’s the
purpose of SMC) but you will need to know their public-facing IP
addresses


There are a few configuration details to take care of:

    1. export TERM=xterm-256color     This will make emacs (provided) much more pleasant.
    2. emacs ~/me    		      	   	     File contains 1 line: your public-facing IP address.
    3. emacs ~/others				     	  	   Public IP addresses of other parties.
    4. Emacs ~/port						   	     	       Port number to run on – 5008 recommended.
    5. Emacs ~/parties								       	    	   List of the IP addresses of all the parties, yourself included.
       	     											   	This is an artifact of old code and will be soon removed.
													     	   	    Used only for key generation.
    6. Emacs ~/ICEES													    	      “1” if using ICEES (healthcare data exchange), else “0”.
    7. source activate impact													      	  We use Anaconda to safely manage python packages but it
 isn’t strictly necessary (dependencies are met by the VM
 image).
    8. Export FLASK_APP=flaskr		Name of the application...
    9. flask run –host=0.0.0.0 –port=5008    ...and run it.





### Installation from GitHub Project

TODO




### ImPACT SMC/MPC Architecture

The ImPACT SMC/MPC implementation consists of only two major
components – a web server (in our case, Flask) and a Secure Multiparty
Computation Engine. The SMC engine is SPDZ/2 from the Bristol (UK)
Cryptography Group. The Flask application calls out to the SMC engine
when it needs to generate new keys or when it wants to initiate a
computation. The installation is the same at each site and,
importantly, there is no “master” site or central hub for
communications – all traffic is peer-to-peer and each site establishes
a connection, on its own, to every other site.

When Flask runs the “flaskr” application, it listens for http requests
on port 5008. Requests can be either for the user-facing web page or
for the REST interface. The web page for users is extremely simple and
is provided as an example of use. The REST interface is used to launch
SMC processes at remote sites. No private or even encrypted
information is ever carried as a web request over HTTP or HTTPS. All
private information flows across the network, encrypted, via SPDZ/2
and its own protocol.

The “flaskr” user-facing web page is
“http://myserver.myuniversity.edu:5008/static/search.html”. This is,
as the name implies, just a completely static page that provides the
user with some instructions and a text box where a study identifier
can be entered. When the user clicks “Submit”, the value of the field
is sent as an HTTP GET to the url
““http://myserver.myuniversity.edu:5008/v2/cohortQuery”. This page
accepts one argument, “ccc”, which is the identifier for the possible
cohort. In our opening example, this value would be
“AliceSmithExperiment31”.

The cohortQuery page, receiving the identifier, proceeds to go to work. The first thing it does is a local database query to determine the potential cohort size for the local site. After finding that number, it proceeds to

1. Read the configuration files to find the names of the other servers
(at the other institutions) and the port number range to work with.

2. Build the REST URLs for the remote sites, using “/v2/cohortQuery”
as the basename, the “ccc” value for the study identifier, “host” to
identify the server that initiated the computation to begin with, and
“party” to tell the remote site whether it’s party 1, party 2, or so
forth. The site that initiated the whole computation is always party
0, and the number carry no meaning except for port number
assignment. The “host” parameter is no longer used and will be removed
in the next release.

3. These URLs are sent to each of the flask servers on the remote
sites. When the cohortCoordinatedQuery page runs, it starts the SPDZ/2
client process and runs it in the background, with the web page
returning immediately. SPDZ/2 handles the asynchronous aspects of the
computation, with a default timeout of 60 seconds.

4. Since the remote requests have been sent to the remote servers, and
the remote SPDZ/2 clients are already running, the page now runs the
SPDZ/2 client itself.

5. All of the clients, one at each site, establishes communications
(every instance communicates with every other instance – there is no
“master”) and uses the SPDZ/2 algorithm to securely compute the sum.

6. The cohortQuery page, now reaching the end of its work, reads the
resulting sum from the SPDZ/2 client and returns it to the user. This
displays in the browser as a line of ASCII text, but of course can be
customized for any fancy HTML desired.

The “/v2/cohortCoordinatedQuery” page is the one that is run at the
remote sites that did not initiate the whole process. The page

1. Queries for the local count of potential participants

2. Runs the SPDZ/2 client (“Player-Online.x”, provided directly by the
SPDZ/2 package). The client runs in the background, waiis until all of
the parties have sent their encrypted values, and executes the
function (“tripleadd”).

3. Returns only a trivial response (“SUCCESS”) because it isn’t meant
for users to call.


TODO – copy the diagrams from the google docs presentations into here.







### THINGS TO KNOW...
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

