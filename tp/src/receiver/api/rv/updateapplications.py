import logging

from json import dumps

from vFense.errorz.error_messages import GenericResults, UpdateApplicationsResults
from vFense.core.api.base import BaseHandler
from vFense.core.decorators import agent_authenticated_request, \
    convert_json_to_arguments

from vFense.plugins.patching.operations.patching_results import PatchingOperationResults

from vFense.receiver.rvhandler import RvHandOff
from vFense.core.user.users import get_user_property
from vFense.core.user import UserKeys

#from server.handlers import *

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvlistener')


class UpdateApplicationsV1(BaseHandler):
    @agent_authenticated_request
    @convert_json_to_arguments
    def put(self, agent_id):
        username = self.get_current_user()
        customer_name = (
            get_user_property(username, UserKeys.CurrentCustomer)
        )
        uri = self.request.uri
        method = self.request.method
        try:
            operation_id = self.arguments.get('operation_id', None)
            error = self.arguments.get('error', None)
            success = self.arguments.get('success', 'true')
            app_data = self.arguments.get('data')
            status_code = self.arguments.get('status_code', None)
            RvHandOff(
               username, customer_name, uri, method, agent_id,
               app_data, oper_type='updates_applications'
            )
            if operation_id:
                print self.arguments
                results = (
                    PatchingOperationResults(
                        username, agent_id,
                        operation_id, success, error,
                        status_code, uri, method
                    )
                )
                results_data = results.apps_refresh()
                print results_data
                results_apps_refresh = results.apps_refresh()
                self.set_status(results_apps_refresh['http_status'])
                self.write(dumps(results_apps_refresh))

            else:
                results = (
                    UpdateApplicationsResults(username, uri, method)
                    .applications_updated(agent_id, app_data)
                )
                results['data'] = []
                self.set_status(results['http_status'])
                self.write(dumps(results))

        except Exception as e:
            results = (
                GenericResults(
                    username, uri, method
                ).something_broke(agent_id, 'udpates_applications', e)
            )
            logger.exception(results)
            self.set_status(results['http_status'])
            self.write(dumps(results))
