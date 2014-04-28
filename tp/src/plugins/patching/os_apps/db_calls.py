from vFense.db.client import db_create_close, r
from vFense.plugins.patching import *
from vFense.plugins.patching._constants import CommonAppKeys
from vFense.core.agent import *
from vFense.errorz.error_messages import GenericResults

import logging
import logging.config

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')


@db_create_close
def get_all_stats_by_appid(username, customer_name,
                           uri, method, app_id,
                           table=AppCollections.AppsPerAgent,
                           conn=None):

    if table == AppCollections.AppsPerAgent:
        CurrentAppsPerAgentCollection = AppCollections.AppsPerAgent
        CurrentAppsPerAgentKey = AppsPerAgentKey
        CurrentAppsPerAgentIndexes = AppsPerAgentIndexes

    elif table == AppCollections.SupportedAppsPerAgent:
        CurrentAppsPerAgentCollection = AppCollections.SupportedAppsPerAgent
        CurrentAppsPerAgentKey = SupportedAppsPerAgentKey
        CurrentAppsPerAgentIndexes = SupportedAppsPerAgentIndexes

    elif table == AppCollections.CustomAppsPerAgent:
        CurrentAppsPerAgentCollection = AppCollections.CustomAppsPerAgent
        CurrentAppsPerAgentKey = CustomAppsPerAgentKey
        CurrentAppsPerAgentIndexes = CustomAppsPerAgentIndexes

    elif table == AppCollections.vFenseAppsPerAgent:
        CurrentAppsPerAgentCollection = AppCollections.vFenseAppsPerAgent
        CurrentAppsPerAgentKey = AgentAppsPerAgentKey
        CurrentAppsPerAgentIndexes = AgentAppsPerAgentIndexes

    try:
        data = []
        apps = (
            r
            .table(CurrentAppsPerAgentCollection)
            .get_all(
                [app_id, customer_name],
                index=CurrentAppsPerAgentIndexes.AppIdAndCustomer
            )
            .group(CurrentAppsPerAgentKey.Status)
            .count()
            .ungroup()
            .run(conn)
        )
        if apps:
            for i in apps:
                new_data = i['reduction']
                new_data = (
                    {
                        CurrentAppsPerAgentKey.Status: i['group'],
                        CommonAppKeys.COUNT: i['reduction'],
                        CommonAppKeys.NAME: i['group'].capitalize()
                    }
                )
                data.append(new_data)

        statuses = map(lambda x: x['status'], data)
        difference = set(CommonAppKeys.ValidPackageStatuses).difference(statuses)
        if len(difference) > 0:
            for status in difference:
                status = {
                    CommonAppKeys.COUNT: 0,
                    CommonAppKeys.STATUS: status,
                    CommonAppKeys.NAME: status.capitalize()
                }
                data.append(status)

        results = (
            GenericResults(
                username, uri, method
            ).information_retrieved(data, len(data))
        )

        logger.info(results)

    except Exception as e:
        results = (
            GenericResults(
                username, uri, method
            ).something_broke('getting_pkg_stats', 'updates', e)
        )

        logger.info(results)
    return(results)


@db_create_close
def get_all_agents_per_appid(username, customer_name,
                             uri, method, app_id,
                             table=AppCollections.AppsPerAgent,
                             conn=None):

    if table == AppCollections.AppsPerAgent:
        CurrentAppsPerAgentCollection = AppCollections.AppsPerAgent
        CurrentAppsPerAgentKey = AppsPerAgentKey

    elif table == AppCollections.SupportedAppsPerAgent:
        CurrentAppsPerAgentCollection = AppCollections.SupportedAppsPerAgent
        CurrentAppsPerAgentKey = SupportedAppsPerAgentKey

    elif table == AppCollections.CustomAppsPerAgent:
        CurrentAppsPerAgentCollection = AppCollections.CustomAppsPerAgent
        CurrentAppsPerAgentKey = CustomAppsPerAgentKey

    elif table == AppCollections.vFenseAppsPerAgent:
        CurrentAppsPerAgentCollection = AppCollections.vFenseAppsPerAgent
        CurrentAppsPerAgentKey = AgentAppsPerAgentKey

    data = []
    try:
        data = []
        agents = (
            r
            .table(CurrentAppsPerAgentCollection)
            .get_all(app_id, index=CurrentAppsPerAgentKey.AppId)
            .eq_join(CurrentAppsPerAgentKey.AgentId, r.table(CurrentAgentsCollection))
            .zip()
            .group(
                lambda x: x[CurrentAppsPerAgentKey.Status]
            )
            .map(
                lambda x:
                {
                    AGENTS:
                    [
                        {
                            AgentKey.ComputerName: x[AgentKey.ComputerName],
                            AgentKey.DisplayName: x[AgentKey.DisplayName],
                            CurrentAppsPerAgentKey.AgentId: x[CurrentAppsPerAgentKey.AgentId]
                        }
                    ],
                    CommonAppKeys.COUNT: 1
                }
            )
            .reduce(
                lambda x, y:
                {
                    AGENTS: x[AGENTS] + y[AGENTS],
                    CommonAppKeys.COUNT: x[COUNT] + y[COUNT]
                }
            )
            .ungroup()
            .run(conn)
        )
        if agents:
            for i in agents:
                new_data = i['reduction']
                new_data[CurrentAppsPerAgentKey.Status] = i['group']
                data.append(new_data)

        statuses = map(lambda x: x['status'], data)
        difference = set(CommonAppKeys.ValidPackageStatuses).difference(statuses)
        if len(difference) > 0:
            for status in difference:
                status = {
                    CommonAppKeys.COUNT: 0,
                    AGENTS: [],
                    CommonAppKeys.STATUS: status
                }
                data.append(status)

        results = (
            GenericResults(
                username, uri, method
            ).information_retrieved(data, len(data))
        )

        logger.info(results)

    except Exception as e:
        results = (
            GenericResults(
                username, uri, method
            ).something_broke('getting_pkg_stats', 'updates', e)
        )

        logger.info(results)

    return(results)


@db_create_close
def get_all_stats_by_agentid(username, customer_name,
                             uri, method, agent_id,
                             table=AppCollections.AppsPerAgent,
                             conn=None):

    if table == AppCollections.AppsPerAgent:
        CurrentAppsPerAgentCollection = AppCollections.AppsPerAgent
        CurrentAppsPerAgentKey = AppsPerAgentKey

    elif table == AppCollections.SupportedAppsPerAgent:
        CurrentAppsPerAgentCollection = AppCollections.SupportedAppsPerAgent
        CurrentAppsPerAgentKey = SupportedAppsPerAgentKey

    elif table == AppCollections.CustomAppsPerAgent:
        CurrentAppsPerAgentCollection = AppCollections.CustomAppsPerAgent
        CurrentAppsPerAgentKey = CustomAppsPerAgentKey

    elif table == AppCollections.vFenseAppsPerAgent:
        CurrentAppsPerAgentCollection = AppCollections.vFenseAppsPerAgent
        CurrentAppsPerAgentKey = AgentAppsPerAgentKey

    try:
        data = []
        apps = (
            r
            .table(CurrentAppsPerAgentCollection)
            .get_all(agent_id, index=CurrentAppsPerAgentKey.AgentId)
            .group(CurrentAppsPerAgentKey.Status)
            .count()
            .ungroup()
            .run(conn)
        )
        if apps:
            for i in apps:
                new_data = i['reduction']
                new_data = (
                    {
                        AppsPerAgentKey.Status: i['group'][CurrentAppsPerAgentKey.Status],
                        CommonAppKeys.COUNT: i['reduction'],
                        CommonAppKeys.NAME: i['group'][CurrentAppsPerAgentKey.Status].capitalize()
                    }
                )
                data.append(new_data)

        statuses = map(lambda x: x['status'], data)
        difference = set(CommonAppKeys.ValidPackageStatuses).difference(statuses)
        if len(difference) > 0:
            for status in difference:
                status = {
                    CommonAppKeys.COUNT: 0,
                    CommonAppKeys.STATUS: status,
                    CommonAppKeys.NAME: status.capitalize()
                }
                data.append(status)

        results = (
            GenericResults(
                username, uri, method
            ).information_retrieved(data, len(data))
        )

        logger.info(results)

    except Exception as e:
        results = (
            GenericResults(
                username, uri, method
            ).something_broke('getting_pkg_stats', 'updates', e)
        )
        logger.info(results)

    return(results)
