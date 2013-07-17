# -*- coding: utf-8 -*-
"""
    sshpool.client
    ~~~~~~~~~~~~~~

    This module provides HTTP client implementation 
    to RESTfully communicate with SSH channels.

    :copyright: (c) 2013 by Abhinav Singh.
    :license: BSD, see LICENSE for more details.
"""
import logging
import requests

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')
logger = logging.getLogger('sshpool.client')

requests_connpool_logger = logging.getLogger('requests.packages.urllib3.connectionpool')
requests_connpool_logger.setLevel(logging.WARNING)

class Client(object):
    
    """SSH channel REST API client."""
    
    def __init__(self, host, port):
        """Initialize REST API client.
        
        Args:
            host (str): SSHPool server interface
            port (int): SSHPool server port
        
        """
        self.host = host
        self.port = port
        self.base_url = 'http://%s:%s' % (self.host, self.port)
    
    def status(self, alias):
        """Retrieve meta info about all initialized SSH channels.
        
        Args:
            alias (str): If provided retrieve meta info for specific SSH channel.
        
        Returns:
            requests.get.
        
        """
        return self.get('/channels/%s' % alias) if alias else self.get('/channels')
    
    def start(self, channel):
        """Start a new SSH channel.
        
        Args:
            channel (str): DSN of format alias://user:pass@host:port.
        
        Returns:
            requests.post.
        
        """
        return self.post('/channels', channel)
    
    def run(self, alias, cmd):
        """Run arbitrary shell command over a SSH channel.
        
        Args:
            alias (str): Channel alias.
            cmd (str): Command to execute.
        
        Returns:
            requests.post.
        
        """
        return self.post('/channels/%s' % alias, cmd)
    
    def stop(self, alias):
        """Stop/terminate a SSH channel.
        
        Args:
            alias (str): Channel alias.
        
        Returns:
            requests.delete.
        
        """
        return self.delete('/channels/%s' % alias)
    
    def url(self, resource):
        """Return full API url for specified resource.
        
        Args:
            resource (str): API resource
        
        Returns:
            str.
        
        """
        return '%s%s' % (self.base_url, resource)
    
    def get(self, resource):
        """Wrapper over requests.get.
        
        Args:
            resource (str): API resource
        
        Returns:
            requests.get.
        
        """
        try:
            return requests.get(self.url(resource))
        except requests.exceptions.ConnectionError, e:
            print e
            return None
    
    def post(self, resource, data):
        """Wrapper over requests.post.
        
        Args:
            resource (str): API resource
        
        Returns:
            requests.post.
        
        """
        try:
            return requests.post(self.url(resource), data=data)
        except requests.exceptions.ConnectionError, e:
            print e
            return None
    
    def delete(self, resource):
        """Wrapper over requests.delete.
        
        Args:
            resource (str): API resource
        
        Returns:
            requests.delete.
        
        """
        try:
            return requests.delete(self.url(resource))
        except requests.exceptions.ConnectionError, e:
            print e
            return None
