# -*- coding: utf-8 -*-
#--------------------------------------------------
#
#     /$$      /$$                     /$$   /$$                        
#    | $$$    /$$$                    |__/  | $$                        
#    | $$$$  /$$$$  /$$$$$$  /$$$$$$$  /$$ /$$$$$$    /$$$$$$   /$$$$$$ 
#    | $$ $$/$$ $$ /$$__  $$| $$__  $$| $$|_  $$_/   /$$__  $$ /$$__  $$
#    | $$  $$$| $$| $$  \ $$| $$  \ $$| $$  | $$    | $$  \ $$| $$  \__/
#    | $$\  $ | $$| $$  | $$| $$  | $$| $$  | $$ /$$| $$  | $$| $$      
#    | $$ \/  | $$|  $$$$$$/| $$  | $$| $$  |  $$$$/|  $$$$$$/| $$      
#    |__/     |__/ \______/ |__/  |__/|__/   \___/   \______/ |__/
#
#     monitor.py
#     This is the main python file for watching
#     uwsgi and nginx log files. Inspired by the
#     tool shown in The Social Network when Mark
#     is monitoring traffic to Facemash.
#
#--------------------------------------------------


# System Imports
#------------------------------------------------------------------------
import os, sys, subprocess
from multiprocessing import Process


# Custom Imports
#------------------------------------------------------------------------
import parser


# PATH Config
#------------------------------------------------------------------------
BASE_PATH = '/var/log/'
LOG_UWSGI = BASE_PATH + 'uwsgi'
LOG_NGINX = BASE_PATH + 'nginx'


# APP Config
#------------------------------------------------------------------------
APP_SITES = {
    'ripeace.org': 'ripeace',
    'ripimg.com': 'ripimg',
    'r1p.com': 'r1p',
    'ripp.org': 'ripp',
    'ripto.com': 'ripto',
    'rip.to': 'rip',
    'rtimg.com': 'rtimg',
    'r.pe': 'r.pe',
    'smaili.org': 'smaili',
    'lt30.com': 'lt30',
}

APP_LOGS = {
    'ripeace': 'ripeace.org.log',
    'ripimg': 'ripimg.com.log',
    'r1p': 'r1p.com.log',
    'ripp': 'ripp.org.log',
    'ripto': 'ripto.com.log',
    'rip': 'rip.to.log',
    'rtimg': 'rtimg.com.log',
    'r.pe': 'r.pe.log',
    'smaili': 'smaili.org.log',
    'lt30': 'lt30.com.log',
    'nginx': 'access.log'
}


# STDOUT Config
#------------------------------------------------------------------------
COLUMNS = int( os.popen('stty size', 'r').read().split()[1] )
COLORS = {
    # Foreground
    'bold': 0,
    'red': 31,
    'green': 32,
    'yellow': 33,
    'blue': 34,
    'magenta': 35,
    'cyan': 36,
    'white': 37,

    # Background
    'red_bg': 41,
    'green_bg': 42,
    'yellow_bg': 43,
    'blue_bg': 44,
    'magenta_bg': 45,
    'cyan_bg': 46,
    'white_bg': 47
}


# Trackers
#------------------------------------------------------------------------
logs = []
files = []


# Functions
#------------------------------------------------------------------------
def color_line(line, app='', color=None):
    if color is None:
        # http://superuser.com/questions/270214/
        if app == 'ripeace':
            color = 'cyan'
        elif app == 'ripimg':
            color = 'green'
        elif app == 'r1p':
            color = 'white'
        elif app == 'ripp':
            color = 'red_bg'
        elif app == 'ripto':
            color = 'green_bg'
        elif app == 'rip':
            color = 'blue_bg'
        elif app == 'rtimg':
            color = 'yellow_bg'
        elif app == 'r.pe':
            color = 'blue'
        elif app == 'smaili':
            color = 'yellow'
        elif app == 'lt30':
            color = 'magenta'

    return "\033[1;%dm%s\033[0m" % (COLORS[color], line)


def join_strings(strings, length=None):
    spacing = COLUMNS / ( length or len(strings) )

    for i,s in enumerate(strings):
        strings[i] = s.ljust(spacing)

    return ''.join(strings)



def parse_line(log, line):
    try :
        if log == 'nginx':
            match = parser.nginx(line)

            strings = [ 
                match[1],
                '->',
                match[2] + ' ' + match[3] + ' ' + match[4],
                match[5],
            ]

            site = match[0]

            # in case non * subdomain like www
            if site.count('.') > 1:
                site = site[ (site.index('.') + 1) : ]

            app = APP_SITES[ site ]

            if app in logs:
                line = join_strings(strings, 5)
                line = color_line( line, app )
            else:
                line = None

        else:
            match = parser.uwsgi(line)

            strings = [ 
                match[0],
                '->',
                match[1] + ' ' + match[2] + ' ' + match[3],
                match[4]
            ]

            line = join_strings(strings, 5)
            line = color_line( line, log )



    except Exception as e:
        line = line.strip()
        line = color_line(line, log)

    if line:
        print line



class Watcher(Process):

    def __init__(self, log, filename):
        super(Watcher, self).__init__()
        self.log = log
        self.filename = filename

    def run(self):
        f = subprocess.Popen( [ 'tail', '-F', self.filename ], stdout=subprocess.PIPE, stderr=subprocess.PIPE )
        while True:
            try:
                line = f.stdout.readline()
                parse_line(self.log, line)
            except KeyboardInterrupt:
                break


def monitor(logs, files):
    watchers = []
    for i in range( len(logs) ):
        if logs[i] == 'nginx':
            base_path = LOG_NGINX
        else:
            base_path = LOG_UWSGI
        files[i] = base_path + '/' + files[i]

        w = Watcher(logs[i], files[i])
        watchers.append(w)
        w.start()

    for w in watchers:
        try:
            w.join()
        except KeyboardInterrupt:
            pass


# Main
#------------------------------------------------------------------------
if __name__=="__main__":
    try:
        args = sys.argv
        log = args[1]

        if log == 'all':
            logs = APP_LOGS.keys()
            files = APP_LOGS.values()
        else:
            logs.append( 'nginx' )
            files.append( APP_LOGS['nginx'] )
            for i in range(1, len(args)):
                logs.append( args[i] )
                files.append( APP_LOGS[ args[i] ] )


        try:
            monitor(logs, files)
        except KeyboardInterrupt:
            pass

    except:
        options = "%s|all" % ( "|".join(APP_LOGS.keys()) )
        print ""
        print color_line("To use: python monitor.py [%s]" % options, color='red')
        print ""