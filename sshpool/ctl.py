# -*- coding: utf-8 -*-
"""
    sshpool.ctl
    ~~~~~~~~~~~

    This module maintain pool of SSH channels and allow communication via RESTful API

    :copyright: (c) 2013 by Abhinav Singh.
    :license: BSD, see LICENSE for more details.
"""
import sys
import cmd
import time
import logging

from .client import Client

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')
logger = logging.getLogger('sshpool.ctl')

class Ctl(cmd.Cmd):
    
    ruler = '~'
    prompt = 'sshpool> '
    intro = '==> Press Ctrl-C to exit <=='
    
    def __init__(self, host, port):
        cmd.Cmd.__init__(self)
        self.host = host
        self.port = port
        self.client = Client(self.host, self.port)
    
    def out(self, line):
        if line is not None:
            if isinstance(line, unicode):
                line = line.encode('utf-8')
            self.stdout.write('%s\n' % line)
    
    def do_status(self, alias):
        r = self.client.status(alias)
        
        if r is None: 
            return
        
        if r.status_code == 200:
            resp = r.json()
            for alias in resp:
                info = resp[alias]
                dsn = '%s:%s@%s:%s' % (info['user'], info['pass'], info['host'], info['port'])
                status = "running" if info['is_alive'] else "dead"
                uptime = int(time.time() - info['start_time'])
                self.out('%s\t\t%s\t%s\t%s' % (alias, dsn, status, uptime))
        else:
            self.out(r.status_code)
    
    def help_status(self):
        self.out('status\t\tView status of started channels')
    
    def do_start(self, dsn):
        r = self.client.start(dsn)
        if r is None: 
            return
        
        if r.status_code == 200:
            self.out(r.text)
        else:
            self.out(r.status_code)
    
    def help_start(self):
        self.out('start <dsn>\tAdd a new channel')
    
    def do_run(self, arg):
        args = arg.split()
        alias = args[0]
        cmd = ' '.join(args[1:])
        
        r = self.client.run(alias, cmd)
        if r is None: 
            return
        
        if r.status_code == 200:
            resp = r.json()
            if resp['exit_code'] == 0:
                self.out(resp['stdout'])
            else:
                self.out(resp['stderr'])
        else:
            self.out(r.status_code)
    
    def help_run(self):
        self.out('run <alias> <cmd>\tRun arbitrary commands over a channel')
    
    def do_stop(self, alias):
        r = self.client.stop(alias)
        
        if r is None: 
            return
        
        if r.status_code == 200:
            self.out(r.text)
        else:
            self.out(r.status_code)
    
    def help_stop(self):
        self.out('stop <alias>\tStop an existing channel')
    
    def do_exit(self, arg):
        sys.exit(0)
    
    def help_exit(self):
        self.out('exit\t\tExit sshpoolctl shell')
    
    do_quit = do_exit
    
    def help_quit(self):
        self.out('quit\t\tExit sshpoolctl shell')
    
    def help_help(self):
        self.out("help\t\tPrint a list of available actions")
        self.out("help <action>\tPrint help for <action>")
    
    def emptyline(self):
        pass
