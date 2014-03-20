import logging
import tornado.httpserver
import tornado.web
from json import dumps
from vFense.agent.agents import update_agent_status
from vFense.errorz.error_messages import GenericResults, AgentResults
from vFense.server.handlers import BaseHandler
from vFense.server.hierarchy.decorators import agent_authenticated_request
from vFense.server.hierarchy.manager import get_current_customer_name

from vFense.receiver.corehandler import process_queue_data

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvlistener')


class CheckInV1(BaseHandler):
    @agent_authenticated_request
    def get(self, agent_id):
        username = self.get_current_user()
        customer_name = get_current_customer_name(username)
        uri = self.request.uri
        method = self.request.method
        try:
            agent_queue = (
                process_queue_data(
                    agent_id, username, customer_name, uri, method
                )
            )
            status = (
                AgentResults(
                    username, uri, method
                ).check_in(agent_id, agent_queue)
            )
            logger.info(status)
            update_agent_status(
                agent_id, username, self.request.uri,
                self.request.method
            )
            self.set_status(status['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(dumps(status))

        except Exception as e:
            status = (
                GenericResults(
                    username, uri, method
                ).something_broke(agent_id, 'check_in', e)
            )
            logger.exception(e)
            self.set_status(status['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(dumps(status))

