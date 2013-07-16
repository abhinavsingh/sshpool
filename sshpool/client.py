# -*- coding: utf-8 -*-
"""
    sshpool.client
    ~~~~~~~~~~~~~~

    This module maintain pool of SSH channels and allow communication via RESTful API

    :copyright: (c) 2013 by Abhinav Singh.
    :license: BSD, see LICENSE for more details.
"""
import logging
import requests

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')
logger = logging.getLogger('sshpool.client')

requests_connpool_logger = logging.getLogger('requests.packages.urllib3.connectionpool')
requests_connpool_logger.setLevel(logging.WARNING)

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