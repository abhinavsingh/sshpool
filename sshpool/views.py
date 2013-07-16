# -*- coding: utf-8 -*-
"""
    sshpool.views
    ~~~~~~~~~~~~~

    This module provides HTTP views implementing available RESTful API's.

    :copyright: (c) 2013 by Abhinav Singh.
    :license: BSD, see LICENSE for more details.
"""
import logging
from flask import Response, request, jsonify
from flask.views import MethodView
from channel import Channel

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')
logger = logging.getLogger('sshpool.views')

class API(MethodView):
    
    """REST API view."""
    
    def get(self, alias):
        """Retrieve meta info for one or all SSH channels."""
        if alias:
            if alias not in Channel.channels:
                return Response('NOT FOUND', 400)
            
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
            _chan = Channel.init(channel)
            return 'OK'
        
        if alias not in Channel.channels:
            return Response('NOT FOUND', 400)
        
        chan = Channel.channels[alias]
        if not chan.is_alive():
            chan = Channel.init(str(chan))
        
        cmd = request.data
        chan.send(cmd)
        return chan.recv()
    
    def delete(self, alias):
        """Stop/terminate a previously configured SSH channel."""
        if alias not in Channel.channels:
            return Response('NOT FOUND', 400)
        
        chan = Channel.channels[alias]
        chan.terminate()
        del Channel.channels[alias]
        return 'OK'
