# -*- coding: utf-8 -*-

#--------------------------------------------------
#
#   Parser.py
#   Parses different kind of log files
#
#--------------------------------------------------


# System
import re





def nginx(line):
    # $server_name ($remote_addr)        ->          $request_method $request_uri          $status          $http_user_agent
    match = re.findall(r''
               '[*.]*' # ignore possible *. in front of server name
               '(\S+)\s' # server name
               '\((.+)\)\s+\-\>\s+' # ip address
               '(\w+|-+)\s' # method
               '(\S+|-+)\s+' # uri
               '(\d+)\s+' # status
               '(.+)' #user agent
            , line)

    return match[0]


def uwsgi(line):
    # (%(addr))        ->          %(method) %(uri)          %(status)          %(msecs) msecs
    match = re.findall(r''
               '\((.+)\)\s+\-\>\s+' # ip address
               '(\w+)\s' # method
               '(\S+)\s+' # uri
               '(\d+)\s+' # status
               '(\d+)\smsecs' # status
            , line)

    return match[0]
