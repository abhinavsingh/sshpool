# -*- coding: utf-8 -*-
"""
    sshpool.sshpoolctl
    ~~~~~~~~~~~~~~~~~~

    Controller script to communicate with SSH channels via RESTful API or an interactive shell

    :copyright: (c) 2013 by Abhinav Singh.
    :license: BSD, see LICENSE for more details.
"""
import cmd
import argparse
import requests
import readline

class Ctl(cmd.Cmd):
    
    def __init__(self, host, port, alias):
        cmd.Cmd.__init__(self)
        self.host = host
        self.port = port
        self.alias = alias
        self.prompt = '%s$ ' % self.alias
    
    def default(self, cmd):
        try:
            print requests.post('http://%s:%s/channel/%s' % (self.host, self.port, self.alias), data=cmd).text
        except requests.exceptions.ConnectionError, e:
            print e
    
    def do_help(self, arg):
        pass

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--alias', help='Channel alias')
    parser.add_argument('--host', default='127.0.0.1', help='SSHPool interface (default: 127.0.0.1)')
    parser.add_argument('--port', default=8877, type=int, help='SSHPool listening port (default: 8877)')
    args = parser.parse_args()
    
    try:
        ctl = Ctl(args.host, args.port, args.alias)
        ctl.cmdloop()
    except KeyboardInterrupt, e:
        pass
    except Exception, e:
        print e

if __name__ == '__main__':
    main()