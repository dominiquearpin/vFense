import tornado.httpserver
import tornado.web
import simplejson as json

import logging
import logging.config
from vFense.core.api.base import BaseHandler
from vFense.db.client import *
from vFense.errorz.error_messages import GenericResults
from vFense.errorz.status_codes import GenericCodes
from vFense.reports.filter_reports import *
from vFense.server.hierarchy.manager import get_current_customer_name
from vFense.server.hierarchy.decorators import authenticated_request, permission_check
from vFense.server.hierarchy.permissions import Permission
from vFense.utils.common import *
from vFense.server.hierarchy.decorators import convert_json_to_arguments
from datetime import datetime

from jsonpickle import encode

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')

class AgentsOsQueryDetailsHandler(BaseHandler):
    @authenticated_request 
    def get(self):
        username = self.get_current_user()
        customer_name = get_current_customer_name(username)
        uri=self.request.uri
        method=self.request.method
        try:
            key=self.get_argument('key')
            query=self.get_argument('query')
            results = systems_os_details(username=username, customer_name=customer_name,
                    key=key,query=query, uri=uri, method=method)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                    GenericResults(
                        username, uri, method
                        ).something_broke('no stats', '', e)
                    )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

class AgentsHardwareQueryDetailsHandler(BaseHandler):
    @authenticated_request
    def get(self):
        username = self.get_current_user()
        customer_name = get_current_customer_name(username)
        uri=self.request.uri
        method=self.request.method
        try:
            results= None
            key=self.get_argument('key')
            query=self.get_argument('query')
            results = systems_hardware_details(username=username, customer_name=customer_name, 
                    key=key, query=query, 
                    uri=uri, method=method)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                    GenericResults(
                        username, uri, method
                        ).something_broke('no stats', '', e)
                    )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

class AgentsCPUQueryDetailsHandler(BaseHandler):
    @authenticated_request
    def get(self):
        username = self.get_current_user()
        customer_name = get_current_customer_name(username)
        uri=self.request.uri
        method=self.request.method
        try:
            results= None
            key=self.get_argument('key')
            query=self.get_argument('query')
            results = systems_cpu_details(username=username, customer_name=customer_name,
                    query=query, key=key,
                    uri=uri, method=method
                    )
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                    GenericResults(
                        username, uri, method
                        ).something_broke('no stats', '', e)
                    )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

class AgentsMemoryQueryDetailsHandler(BaseHandler):
    @authenticated_request
    def get(self):
        username = self.get_current_user()
        customer_name = get_current_customer_name(username)
        uri=self.request.uri
        method=self.request.method
        try:
            results= None
            key=self.get_argument('key')
            query=self.get_argument('query')
            results = systems_memory_stats(username=username, customer_name=customer_name,
                    query=query, key=key,
                    uri=uri, method=method,
                    )
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                    GenericResults(
                        username, uri, method
                        ).something_broke('no stats', '', e)
                    )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

class AgentsDiskQueryDetailsHandler(BaseHandler):
    @authenticated_request
    def get(self):
        username = self.get_current_user()
        customer_name = get_current_customer_name(username)
        uri=self.request.uri
        method=self.request.method
        try:
            results= None
            key=self.get_argument('key')
            query=self.get_argument('query')
            results = systems_disk_stats(username=username, customer_name=customer_name,
                    query=query, key=key,
                    uri=uri, method=method
                    )
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                    GenericResults(
                        username, uri, method
                        ).something_broke('no stats', '', e)
                    )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

class AgentsNetworkQueryDetailsHandler(BaseHandler):
    @authenticated_request
    def get(self):
        username = self.get_current_user()
        customer_name = get_current_customer_name(username)
        uri=self.request.uri
        method=self.request.method
        try:
            results= None
            key=self.get_argument('key')
            query=self.get_argument('query')
            results = systems_network_details(username=username, customer_name=customer_name,
                    query=query, key=key,
                    uri=uri, method=method
                    )
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                    GenericResults(
                        username, uri, method
                        ).something_broke('no stats', '', e)
                    )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))                    

class AgentsLastUpdatedHandler(BaseHandler):
    @authenticated_request
    def get(self):
        username = self.get_current_user()
        customer_name = get_current_customer_name(username)
        uri=self.request.uri
        method=self.request.method
        try:
            results= None
            key=self.get_argument('key')
            query=self.get_argument('query')
            results = agents_last_updated(username=username, customer_name=customer_name,
                    query=query, key=key,
                    uri=uri, method=method
                    )
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                    GenericResults(
                        username, uri, method
                        ).something_broke('no stats', '', e)
                    )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4)) 


class AgentsRequireRebootHandler(BaseHandler):
    @authenticated_request
    def get(self):
        username = self.get_current_user()
        customer_name = get_current_customer_name(username)
        uri=self.request.uri
        method=self.request.method
        try:
            results= None
            key=self.get_argument('key')
            query=self.get_argument('query')
            results = agents_reboot_pending(username=username, customer_name=customer_name,
                    query=query, key=key,
                    uri=uri, method=method
                    )
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                    GenericResults(
                        username, uri, method
                        ).something_broke('no stats', '', e)
                    )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))


class AgentsConnectionStatusHandler(BaseHandler):
    @authenticated_request
    def get(self):
        username = self.get_current_user()
        customer_name = get_current_customer_name(username)
        uri=self.request.uri
        method=self.request.method
        try:
            results= None
            key=self.get_argument('key')
            query=self.get_argument('query')
            results = agents_status(username=username, customer_name=customer_name,
                    query=query, key=key,
                    uri=uri, method=method
                    )
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                    GenericResults(
                        username, uri, method
                        ).something_broke('no stats', '', e)
                    )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))                    

