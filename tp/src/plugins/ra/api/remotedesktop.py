import json

from vFense.server.handlers import BaseHandler
from vFense.server.hierarchy.permissions import Permission
from vFense.server.hierarchy.decorators import authenticated_request, permission_check

from vFense.plugins import ra
from vFense.plugins.ra import creator


class RDSession(BaseHandler):

    @permission_check(permission=Permission.RemoteAssistance)
    def post(self):

        current_user = self.get_current_user()
        body = json.loads(self.request.body)
        agent_id = body.get('agent_id')

        results = creator.new_rd_session(
            agent_id=agent_id,
            user=current_user
        )

        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results, indent=4))

    @permission_check(permission=Permission.RemoteAssistance)
    def delete(self):

        current_user = self.get_current_user()
        body = json.loads(self.request.body)
        agent_id = body.get('agent_id')

        results = creator.terminate_rd_session(
            agent_id=agent_id,
            user=current_user
        )

        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results, indent=4))
