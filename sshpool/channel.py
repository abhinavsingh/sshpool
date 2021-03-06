# -*- coding: utf-8 -*-
"""
    sshpool.channel
    ~~~~~~~~~~~~~~~

    This module provides capability to spawn SSH channels in
    a separate process and ability to execute arbitrary
    shell commands by communicating over pipe.

    :copyright: (c) 2013 by Abhinav Singh.
    :license: BSD, see LICENSE for more details.
"""
import time
import socket
import logging
import getpass
import paramiko
import multiprocessing

try:
    import urllib.parse as urlparse
except ImportError:
    import urlparse

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')
logger = logging.getLogger('sshpool.channel')

paramiko_transport_logger = logging.getLogger('paramiko.transport')
paramiko_transport_logger.setLevel(logging.WARNING)

class Channel(multiprocessing.Process):
    
    """Spawn SSH channel and provides communication over pipe.
    
    Attributes:
        channel (str): DSN of format alias://user:pass@host:port.
    
    """
    
    channels = dict()
    
    def __init__(self, channel):
        """Initialize a new SSH channel.
        
        Args:
            channel (str): DSN of format alias://user:pass@host:port.
        
        """
        multiprocessing.Process.__init__(self)
        chan = urlparse.urlparse(channel)
        
        self.alias = chan.scheme
        assert self.alias is not ''
        
        self.username = chan.username if chan.username else getpass.getuser()
        self.password = chan.password
        self.hostname = chan.hostname
        self.port = chan.port if chan.port else 22
        
        self.inner, self.outer = multiprocessing.Pipe(duplex=True)
        self.client = None
        self.daemon = True
        
        self.start_time = time.time()
    
    def connect(self):
        """Establish SSH channel. Raises exception in case of failure."""
        try:
            logger.info('connecting to %s' % self)
            self.client = paramiko.SSHClient()
            self.client.load_system_host_keys()
            self.client.set_missing_host_key_policy(paramiko.WarningPolicy())
            self.client.connect(self.hostname, self.port, self.username, self.password)
            logger.info('connected to %s' % self)
        except socket.gaierror as e:
            logger.critical('connection to %s failed because host is not known' % self)
            raise
        except paramiko.BadAuthenticationType as e:
            logger.critical('connection to %s failed due to unsupported authentication type, supported types are %s' % (self, ','.join(e.allowed_types)))
            raise
        except paramiko.AuthenticationException as e:
            logger.critical('connection to %s failed due to authentication failure' % self)
            raise
        except Exception as e:  # pragma: no cover
            logger.critical('connection to %s failed with reason %r' % (self, e))
            raise
    
    def exec_command(self, cmd):
        """Wrapper over paramiko.SSHClient.exec_command.
        
        Returns:
            tuple.
        
        """
        stdin, stdout, stderr = self.client.exec_command(cmd)
        stdin.close()
        return stdout.read(), stderr.read(), stdout.channel.recv_exit_status()
    
    def run_once(self):
        """Accept a command and execute over SSH channel, finally queue back command output for calling client."""
        cmd = self.inner.recv()
        stdout, stderr, exit_code = self.exec_command(cmd)
        self.inner.send({
            'stdout': stdout,
            'stderr': stderr,
            'exit_code': exit_code,
        })
    
    def run(self):
        """Execute channel workflow."""
        self.connect()
        try:
            while True:
                self.run_once()
        except paramiko.SSHException as e:
            logger.critical('connection dropped with exception %r' % e)
            self.inner.send({'exception': '%r' % e})
        except KeyboardInterrupt as e:
            logger.info('caught keyboard interrupt, stopping %s' % self)
            self.inner.send({'exception': '%r' % e})
        finally:
            logger.info('closing connection to %s' % self)
            self.client.close()
    
    @staticmethod
    def init(channel, start=True):
        """API to initialize and optionally start a new SSH channel.
        
        Args:
            channel (str): DSN of format alias://user:pass@host:port.
        
        Kwargs:
            start (bool): Whether to start initialized SSH channel.
        
        Returns:
            Channel.
        
        It is highly recommended to use this API to initialize SSH channels 
        as it also updates global channel registry required for communication 
        over RESTful API.
        
        """
        chan = Channel(channel)
        Channel.channels[chan.alias] = chan
        if start: 
            chan.start()
        return chan
    
    def send(self, cmd):
        """API to execute arbitrary commands over SSH channel.
        
        Args:
            cmd (str): Command to execute.
        
        """
        logger.debug('sending command %s' % cmd)
        self.outer.send(cmd)
    
    def recv(self):
        """API to receive output of last executed command over SSH channel.
        
        Returns:
            dict. A dictionary containing stdout, stderr and exit code of executed command.
        
        """
        ret = self.outer.recv()
        logger.debug('receiving response %s' % ret)
        return ret
    
    def info(self):
        """API to grab meta info about SSH channel.
        
        Returns:
            dict.
        
        """
        return {
            'user': self.username,
            'pass': self.password,
            'host': self.hostname,
            'port': self.port,
            'is_alive': self.is_alive(),
            'start_time': self.start_time,
        }
    
    def stop(self):
        """API to terminate SSH channel.
        
        It is highly recommended to use this API to terminate SSH channel
        process as it also updates global channel registry.
        
        """
        self.terminate()
        del Channel.channels[self.alias]
    
    def __str__(self):
        return '%s://%s:%s@%s:%s' % (self.alias, self.username, self.password, self.hostname, self.port)
