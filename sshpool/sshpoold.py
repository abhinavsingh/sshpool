# -*- coding: utf-8 -*-
"""
    sshpool.sshpoold
    ~~~~~~~~~~~~~~~~

    Maintains pool of SSH channels and allow communication via RESTful API

    :copyright: (c) 2013 by Abhinav Singh.
    :license: BSD, see LICENSE for more details.
"""
import argparse
import urlparse
import multiprocessing
import paramiko
import logging
import getpass
import flask

web = flask.Flask('sshpool')

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')
logger = logging.getLogger('sshpool')

class Channel(multiprocessing.Process):
    
    channels = dict()
    
    def __init__(self, channel):
        multiprocessing.Process.__init__(self)
        chan = urlparse.urlparse(channel)
        
        self.alias = chan.scheme
        self.username = chan.username if chan.username else getpass.getuser()
        self.password = chan.password
        self.hostname = chan.hostname
        self.port = chan.port if chan.port else 22
        
        self.inner, self.outer = multiprocessing.Pipe(duplex=True)
        self.client = None
        self.daemon = True
    
    @staticmethod
    def init(channel):
        chan = Channel(channel)
        Channel.channels[chan.alias] = chan
        return chan
    
    def connect(self):
        logger.info('connecting to %s' % self)
        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(paramiko.WarningPolicy())
        self.client.connect(self.hostname, self.port, self.username, self.password)
    
    def send(self, cmd):
        logger.debug('sending command %s' % cmd)
        self.outer.send(cmd)
    
    def recv(self):
        ret = self.outer.recv()
        logger.debug('receiving response %s' % ret)
        return ret
    
    def run(self):
        try:
            self.connect()
            logger.info('connected to %s' % self)
        except paramiko.AuthenticationException, e:
            logger.critical('connection to %s failed due to authentication failure' % self)
            raise
        except Exception, e:
            logger.critical('connection to %s failed with reason %r' % (self, e))
            raise
        
        try:
            while True:
                cmd = self.inner.recv()
                stdin, stdout, stderr = self.client.exec_command(cmd)
                err = stderr.read()
                out = stdout.read()
                ret = out if len(err) == 0 else err
                self.inner.send(ret)
        except paramiko.SSHException, e:
            logger.critical('connection dropped with exception %r' % e)
            self.inner.send('%r' % e)
        except KeyboardInterrupt, e:
            pass
        
        self.client.close()
    
    def __str__(self):
        return '%s://%s:%s@%s:%s' % (self.alias, self.username, self.password, self.hostname, self.port)

@web.route('/channel/<alias>', methods=['POST'])
def handle_commands(alias):
    if alias not in Channel.channels:
        return flask.Response('Not found', 400)
    
    chan = Channel.channels[alias]
    if not chan.is_alive():
        chan = Channel.init(str(chan))
        chan.start()
    
    cmd = flask.request.data
    chan.send(cmd)
    return chan.recv()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--channel', action='append', help='alias://user:pass@host:port')
    parser.add_argument('--host', default='127.0.0.1', help='SSHPool interface (default: 127.0.0.1)')
    parser.add_argument('--port', default=8877, type=int, help='SSHPool listening port (default: 8877)')
    args = parser.parse_args()
    
    for channel in args.channel:
        chan = Channel.init(channel)
        chan.start()
    
    web.run(host=args.host, port=args.port, debug=False)
    
    for alias in Channel.channels:
        chan = Channel.channels[alias]
        chan.join()
    
    print 'done!'

if __name__ == '__main__':
    main()