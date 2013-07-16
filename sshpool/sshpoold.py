# -*- coding: utf-8 -*-
"""
    sshpool.sshpoold
    ~~~~~~~~~~~~~~~~

    This module maintain pool of SSH channels and allow communication via RESTful API

    :copyright: (c) 2013 by Abhinav Singh.
    :license: BSD, see LICENSE for more details.
"""
import argparse
from channel import Channel
from http import Http

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--channel', default=list(), action='append', help='alias://user:pass@host:port')
    parser.add_argument('--host', default='127.0.0.1', help='SSHPool interface (default: 127.0.0.1)')
    parser.add_argument('--port', default=8877, type=int, help='SSHPool listening port (default: 8877)')
    args = parser.parse_args()
    
    for channel in args.channel:
        _chan = Channel.init(channel)
    
    Http().start(args.host, args.port)
    
    for alias in Channel.channels:
        chan = Channel.channels[alias]
        chan.join()
    
    print 'done!'

if __name__ == '__main__':
    main()
