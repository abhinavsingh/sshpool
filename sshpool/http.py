# -*- coding: utf-8 -*-
"""
    sshpool.http
    ~~~~~~~~~~~~

    This module maintain pool of SSH channels and allow communication via RESTful API

    :copyright: (c) 2013 by Abhinav Singh.
    :license: BSD, see LICENSE for more details.
"""
import logging
from flask import Flask
from views import API

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')
logger = logging.getLogger('sshpool.http')

class Http(object):
    
    def __init__(self):
        self.web = Flask('sshpool')
        self.enable_channel_api()
    
    def enable_channel_api(self):
        view = API.as_view('api')
        self.web.add_url_rule('/channels', defaults={'alias': None}, view_func=view, methods=['GET', ])
        self.web.add_url_rule('/channels/<alias>', view_func=view, methods=['GET', ])
        self.web.add_url_rule('/channels', defaults={'alias': None}, view_func=view, methods=['POST', ])
        self.web.add_url_rule('/channels/<alias>', view_func=view, methods=['POST', ])
        self.web.add_url_rule('/channels/<alias>', view_func=view, methods=['DELETE', ])
    
    def start(self, host, port, debug=False):
        self.web.run(host=host, port=port, debug=debug)
