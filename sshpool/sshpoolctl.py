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

class API(object):
    
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.base_url = 'http://%s:%s' % (self.host, self.port)
    
    def status(self, alias):
        return self.get('/channels/%s' % alias) if alias else self.get('/channels')
    
    def start(self, dsn):
        return self.post('/channels', dsn)
    
    def run(self, alias, cmd):
        return self.post('/channels/%s' % alias, cmd)
    
    def stop(self, alias):
        return self.delete('/channels/%s' % alias)
    
    def url(self, resource):
        return '%s%s' % (self.base_url, resource)
    
    def get(self, resource):
        try:
            return requests.get(self.url(resource))
        except requests.exceptions.ConnectionError, e:
            print e
            return None
    
    def post(self, resource, data):
        try:
            return requests.post(self.url(resource), data=data)
        except requests.exceptions.ConnectionError, e:
            print e
            return None
    
    def delete(self, resource):
        try:
            return requests.delete(self.url(resource))
        except requests.exceptions.ConnectionError, e:
            print e
            return None

class Ctl(cmd.Cmd):
    
    ruler = '~'
    prompt = 'sshpool> '
    intro = '==> Press Ctrl-C to exit <=='
    
    def __init__(self, host, port):
        cmd.Cmd.__init__(self)
        self.host = host
        self.port = port
        self.api = API(self.host, self.port)
    
    def out(self, line):
        if line is not None:
            if isinstance(line, unicode):
                line = line.encode('utf-8')
            self.stdout.write(line + '\n')
    
    def do_status(self, alias):
        r = self.api.status(alias)
        if r is None: return
        if r.status_code == 200:
            resp = r.json()
            for alias in resp:
                info = resp[alias]
                dsn = '%s:%s@%s:%s' % (info['username'], info['password'], info['hostname'], info['port'])
                status = "running" if info['is_alive'] else "dead"
                uptime = info['uptime']
                self.out('%s\t\t%s\t%s\t%s' % (alias, dsn, status, uptime))
        else:
            self.out(r.status_code)
    
    def help_status(self):
        self.out('status\t\tView status of started channels')
    
    def do_start(self, dsn):
        r = self.api.start(dsn)
        if r is None: return
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
        r = self.api.run(alias, cmd)
        if r is None: return
        if r.status_code == 200:
            self.out(r.text)
        else:
            self.out(r.status_code)
    
    def help_run(self):
        self.out('run <alias> <cmd>\tRun arbitrary commands over a channel')
    
    def do_stop(self, alias):
        r = self.api.stop(alias)
        if r is None: return
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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1', help='SSHPool interface (default: 127.0.0.1)')
    parser.add_argument('--port', default=8877, type=int, help='SSHPool listening port (default: 8877)')
    args = parser.parse_args()
    
    try:
        ctl = Ctl(args.host, args.port)
        ctl.cmdloop()
    except KeyboardInterrupt, e:
        pass
    except Exception, e:
        print e
    
    print 'done!'

if __name__ == '__main__':
    main()