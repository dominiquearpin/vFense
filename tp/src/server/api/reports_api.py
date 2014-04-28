import simplejson as json

import logging
import logging.config
from vFense.core.api.base import BaseHandler
from vFense.db.client import *
from vFense.errorz.error_messages import GenericResults
from reports.stats import *
from vFense.core.decorators import authenticated_request
from vFense.utils.common import *
from vFense.core.user import UserKeys
from vFense.core.user.users import get_user_property

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')

class AgentsOsDetailsHandler(BaseHandler):
    @authenticated_request 
    def get(self):
        username = self.get_current_user()
        customer_name = (
            get_user_property(username, UserKeys.CurrentCustomer)
        )
        uri=self.request.uri
        method=self.request.method
        try:
            os_code=self.get_argument('os_code', None)
            tag_id=self.get_argument('tag_id', None)
            results = systems_os_details(username=username, customer_name=customer_name,
                    os_code=None,tag_id=None, uri=uri, method=method)
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

class AgentsHardwareDetailsHandler(BaseHandler):
    @authenticated_request
    def get(self):
        username = self.get_current_user()
        customer_name = (
            get_user_property(username, UserKeys.CurrentCustomer)
        )
        uri=self.request.uri
        method=self.request.method
        try:
            results= None
            os_code=self.get_argument('os_code', None)
            tag_id=self.get_argument('tag_id', None)
            results = systems_hardware_details(username=username, customer_name=customer_name, 
                    os_code=os_code, tag_id=tag_id, 
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

class AgentsCPUDetailsHandler(BaseHandler):
    @authenticated_request
    def get(self):
        username = self.get_current_user()
        customer_name = (
            get_user_property(username, UserKeys.CurrentCustomer)
        )
        uri=self.request.uri
        method=self.request.method
        try:
            results= None
            os_code=self.get_argument('os_code', None)
            tag_id=self.get_argument('tag_id', None)
            results = systems_cpu_details(username=username, customer_name=customer_name,
                    tag_id=tag_id, os_code=os_code,
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

class AgentsMemoryDetailsHandler(BaseHandler):
    @authenticated_request
    def get(self):
        username = self.get_current_user()
        customer_name = (
            get_user_property(username, UserKeys.CurrentCustomer)
        )
        uri=self.request.uri
        method=self.request.method
        try:
            results= None
            os_code=self.get_argument('os_code', None)
            tag_id=self.get_argument('tag_id', None)
            results = systems_memory_stats(username=username, customer_name=customer_name,
                    tag_id=tag_id, os_code=os_code,
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

class AgentsDiskDetailsHandler(BaseHandler):
    @authenticated_request
    def get(self):
        username = self.get_current_user()
        customer_name = (
            get_user_property(username, UserKeys.CurrentCustomer)
        )
        uri=self.request.uri
        method=self.request.method
        try:
            results= None
            os_code=self.get_argument('os_code', None)
            tag_id=self.get_argument('tag_id', None)
            results = systems_disk_stats(username=username, customer_name=customer_name,
                    tag_id=tag_id, os_code=os_code,
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

class AgentsNetworkDetailsHandler(BaseHandler):
    @authenticated_request
    def get(self):
        username = self.get_current_user()
        customer_name = (
            get_user_property(username, UserKeys.CurrentCustomer)
        )
        uri=self.request.uri
        method=self.request.method
        try:
            results= None
            os_code=self.get_argument('os_code', None)
            tag_id=self.get_argument('tag_id', None)
            results = systems_network_details(username=username, customer_name=customer_name,
                    tag_id=tag_id, os_code=os_code,
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
