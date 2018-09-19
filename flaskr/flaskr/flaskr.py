# all the imports
import os
import sqlite3
import sys
import subprocess
import re
import runpy

import urllib.request
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from socket import gethostname


app = Flask(__name__, static_url_path='/static') # create the application instance :)
app.config.from_object(__name__) # load config from this file , flaskr.py

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')

#@app.route('/')
#def show_entries():
#    db = get_db()
#    cur = db.execute('select title, text from entries order by id desc')
#    entries = cur.fetchall()
#    return render_template('show_entries.html', entries=entries)

@app.route('/vvv/tester')
def tester():
    ccc = request.args.get('ccc', None)
    print (ccc)
    return ("tester: ok.")


@app.route('/v2/cohortQuery')
def cohortQuery():
    print('INCOHORTQUERY')
    requestQueryString = request.query_string.decode('UTF-8')
    print(requestQueryString)
    ccc = request.args.get('ccc', '0')

# First Step: do our own database query for cohort count
    conn = sqlite3.connect(app.config['DATABASE'])
    c=conn.cursor()
    query ="select candidatecount from candidates where study = '" + ccc + "' ;"
    print('Query='+ query)
    c.execute(query)
    data=c.fetchone()
    if data is None:
        localCount = 222222
    else:
        localCount = int(data[0])
    localCountResultString = str(localCount)

# Secondly: start the Server.x process to assign SPDZ connections to clients

#    serverxcmd = '/home/ec2-user/impact-bin/startServer.sh'
#    CallerResult = subprocess.run(serverxcmd, shell = True, stdout=subprocess.PIPE)

# read all other servers
    with open('/home/ec2-user/others') as f:
        others = f.read().splitlines()
    with open('/home/ec2-user/me') as g:
        me = g.read().splitlines()

# Third: start the remote queries that fetch their value and use the SPDZ client
# to do their computations. We don't even care about the return values.

    qstr=[]
    qstr.append('http://' + others[0].strip() + '/v2/cohortCoordinatedQuery?ccc=' + ccc + '&host=' + me[0].strip() + '&party=1')
    qstr.append('http://' + others[1].strip() + '/v2/cohortCoordinatedQuery?ccc=' + ccc + '&host=' + me[0].strip() + '&party=2')

#    print('IT EQUALS: http://' + others[0].strip() + '/v2/cohortCoordinatedQuery?ccc=' + ccc + '&host=' + me[0].strip() + '&party=1')
#    print('IT EQUALS: http://' + others[1].strip() + '/v2/cohortCoordinatedQuery?ccc=' + ccc + '&host=' + me[0].strip() + '&party=2')
    print('IT EQUALS: ' + qstr[0])
    print('IT EQUALS: ' + qstr[1])

    idx=0
    parties=[]
    for u in others:
        parties.append(u.strip().split(':')[0])
        print ('PARTY ' + parties[idx])
        idx = idx+ 1

#    with urllib.request.urlopen('http://' + others[0].strip() + '/v2/cohortCoordinatedQuery?ccc=' + ccc + '&host=' + me[0].strip() + '&party=1') as f:
#        throwaway = f.read(1000)
#    with urllib.request.urlopen('http://' + others[1].strip() + '/v2/cohortCoordinatedQuery?ccc=' + ccc + '&host=' + me[0].strip() +'&party=2') as f:
#        throwaway = f.read(1000)
    with urllib.request.urlopen(qstr[0]) as f:
        throwaway = f.read(1000)
    with urllib.request.urlopen(qstr[1]) as f:
        throwaway = f.read(1000)

    print('THROWAWAY: ' + throwaway.decode('UTF-8'))

# Fourth: start the SPDZ client with our count. This will return (eventually, 
# after the next few steps run) return the total SMC-computed count.

    clientxcmd = '/home/ec2-user/impact-bin/runSMC.sh ' + localCountResultString + ' ' + me[0].strip()+ ' 0'
    print (clientxcmd)
    CallerResult = subprocess.run(clientxcmd, shell = True, stdout=subprocess.PIPE)

    print('RAN THE SUBPROCESS (runSMC.sh) ')


# Fifth: remember the first SPDZ client, running on the main machine? That's the one
# that returns a value. Read that and print it.

    with open('/tmp/resultTotal') as f:
        theFinalResult = f.read()

    print ('theFinalResult = ' + theFinalResult)
#end of cohortQuery
    return theFinalResult+ '\n'



@app.route('/v2/cohortCoordinatedQuery')
def cohortCoordinatedQuery():
    print('INCOHORTCOORDINATED')
    requestQueryString = request.query_string.decode('UTF-8')
    print(requestQueryString)
    ccc = request.args.get('ccc', '0')
    party = request.args.get('party', '1')
    spdzHost = request.args.get('host', '1')

# First Step: do our own database query for cohort count
    conn = sqlite3.connect(app.config['DATABASE'])
    c=conn.cursor()
    query ="select candidatecount from candidates where study = '" + ccc + "' ;"
    print('Query='+ query)
    c.execute(query)
    data=c.fetchone()
    if data is None:
        localCount = 222222
    else:
        localCount = int(data[0])
    localCountResultString = str(localCount)

    with open('/home/ec2-user/others') as f:                                   
        others = f.read().splitlines()                                         
    with open('/home/ec2-user/me') as g:                                       
        me = g.read().splitlines()           


# Second: start the SPDZ client with our count. This will return (eventually, 
# after the next few steps run) return the total SMC-computed count.

    playercmd = 'nohup /home/ec2-user/impact-bin/runSMC.sh ' + localCountResultString + ' ' + spdzHost.strip()+ ' ' + party + ' >&/dev/null &'
    print ("playercmd = " + playercmd)
    CallerResult = subprocess.run(playercmd, shell = True, stdout=subprocess.PIPE)

    print ('coord query ran the playercmd OK.')

# Third: return a success code - SPDZ/2 is working in the background, we don't know
# if it's going to work or not.


    return 'SUCCESS\n'


@app.route('/v2/createTriples')
def createTriples():
    print('INCOHORTCOORDINATED')
    requestQueryString = request.query_string.decode('UTF-8')
    print(requestQueryString)
    parties = request.args.get('parties', '0')


    triplecmd = 'nohup /home/ec2-user/impact-bin/createTriples.sh &'
    print ("triplecmd = " + triplecmd)
    CallerResult = subprocess.run(triplecmd, shell = True, stdout=subprocess.PIPE)

    return 'SUCCESS\n'





@app.route('/')
def show_usage():
    return render_template('show_usage.html')
#    return render_template('input.html')



