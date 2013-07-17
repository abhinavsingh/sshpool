# -*- coding: utf-8 -*-
"""
    sshpool.rest
    ~~~~~~~~~~~~

    This module provides RESTful API to interact with SSH channels.

    :copyright: (c) 2013 by Abhinav Singh.
    :license: BSD, see LICENSE for more details.
"""
import logging
from flask import Flask, Response, request, jsonify
from flask.views import MethodView

from .channel import Channel

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')
logger = logging.getLogger('sshpool.rest')

class API(MethodView):
    
    """REST API view."""
    
    def get(self, alias):
        """Retrieve meta info for one or all SSH channels."""
        if alias:
            if alias not in Channel.channels:
                return Response('NOT FOUND', 404)
            
            chan = Channel.channels[alias]
            return jsonify(**chan.info())
        
        kwargs = dict()
        for alias in Channel.channels:
            chan = Channel.channels[alias]
            kwargs[alias] = chan.info()
        return jsonify(**kwargs)
    
    def post(self, alias):
        """Start a new SSH channel or execute command over a SSH channel."""
        if not alias:
            channel = request.data
            try:
                Channel.init(channel)
                return 'OK'
            except AssertionError, e:
                logger.critical('Unable to start SSH channel due to %r' % e)
                return Response('BAD REQUEST', 400)
        
        if alias not in Channel.channels:
            return Response('NOT FOUND', 404)
        
        chan = Channel.channels[alias]
        if not chan.is_alive():
            logger.info('Channel alias %s is dead, restarting' % alias)
            chan = Channel.init(str(chan))
        chan.send(request.data)
        return jsonify(**chan.recv())
    
    def delete(self, alias):
        """Stop/terminate a previously configured SSH channel."""
        if alias not in Channel.channels:
            return Response('NOT FOUND', 404)
        
        chan = Channel.channels[alias]
        chan.stop()
        return 'OK'

class HTTP(object):
    
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.web = Flask('sshpool')
        self.enable_channel_api()
    
    def enable_channel_api(self):
        view = API.as_view('api')
        self.web.add_url_rule('/channels', defaults={'alias': None}, view_func=view, methods=['GET', ])
        self.web.add_url_rule('/channels/<alias>', view_func=view, methods=['GET', ])
        self.web.add_url_rule('/channels', defaults={'alias': None}, view_func=view, methods=['POST', ])
        self.web.add_url_rule('/channels/<alias>', view_func=view, methods=['POST', ])
        self.web.add_url_rule('/channels/<alias>', view_func=view, methods=['DELETE', ])
    
    def start(self, debug=False):  # pragma: no cover
        self.web.run(host=self.host, port=self.port, debug=debug)
