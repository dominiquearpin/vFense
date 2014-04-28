import logging

from vFense.core._constants import *
from vFense.core._db import retrieve_primary_key
from vFense.core.decorators import return_status_tuple, time_it
from vFense.plugins.patching._constants import CommonFileKeys
from vFense.plugins.patching import AppCollections, DownloadCollections, \
    FileCollections, AppsKey, AppsPerAgentKey, AppsIndexes, \
    AppsPerAgentIndexes, SupportedAppsKey, SupportedAppsPerAgentKey, \
    SupportedAppsPerAgentIndexes, CustomAppsKey, CustomAppsPerAgentKey, \
    CustomAppsPerAgentIndexes, AgentAppsKey, AgentAppsPerAgentKey, \
    AgentAppsPerAgentIndexes, DbCommonAppKeys, DbCommonAppPerAgentKeys, \
    DbCommonAppIndexes, DbCommonAppPerAgentIndexes, FilesKey, \
    FileServerIndexes, FileServerKeys

from vFense.db.client import db_create_close, r

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')


@time_it
@db_create_close
def fetch_file_servers_addresses(customer_name, conn=None):
    """Fetch file servers for customer name. This will
        retrieve a list of addresses (ip_addresses or hostnames)
    Args:
        customer_name (str): The name of the customer

    Basic Usage:
        >>> from vFense.plugins.patching._db import fetch_file_servers_addresses
        >>> customer_name = 'default'
        >>> fetch_file_servers_addresses(customer_name)

    Return:
        List of addresses
    """
    data = []
    try:
        data = list(
            r
            .table(FileCollections.FileServers)
            .get_all(customer_name, index=FileServerIndexes.CustomerName)
            .map(lambda x: x[FileServerKeys.CustomerName])
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return(data)

@time_it
@db_create_close
def fetch_file_data(app_id, agent_id=None, conn=None):
    """Fetch file data for app id or app id and agent id
    Args:
        app_id (str): The 64 character ID of the application.

    Kwargs:
        agent_id (str): The 32 character UUID of the agent

    Basic Usage:
        >>> from vFense.plugins.patching._db import fetch_file_data
        >>> app_id = '15fa819554aca425d7f699e81a2097898b06f00a0f2dd6e8d51a18405360a6eb'
        >>> agent_id = '7f242ab8-a9d7-418f-9ce2-7bcba6c2d9dc'
        >>> fetch_file_data(app_id, agent_id)

    Return:
        Dictionary
    """
    try:
        if agent_id:
            data = list(
                r
                .table(FileCollections.Files)
                .filter(
                    lambda x: (
                        x[FilesKey.AppIds].contains(app_id)
                        &
                        x[FilesKey.AgentIds].contains(agent_id)
                    )
                )
                .without(FilesKey.AppIds, FilesKey.AgentIds,)
                .run(conn)
            )

        else:
            data = list(
                r
                .table(FilesCollection)
                .filter(
                    lambda x: (
                        x[FilesKey.AppIds].contains(app_id)
                    )
                )
                .without(FilesKey.AppIds, FilesKey.AgentIds,)
                .run(conn)
            )

    except Exception as e:
        logger.exception(e)

    return(data)


@db_create_close
def fetch_app_data(
    app_id, table=AppCollections.UniqueApplications,
    fields_to_pluck=None, conn=None
    ):
    """Fetch application data by app id
    Args:
        app_id (str): 64 character ID of the application.

    Kwargs:
        table (str): The name of the apps per agent collection,
            that will be used when updating the application data.

    Basic Usage:
        >>> from vFense.plugins.patching._db import fetch_app_data
        >>> app_id = '15fa819554aca425d7f699e81a2097898b06f00a0f2dd6e8d51a18405360a6eb'
        >>> table = 'unique_applications'
        >>> fetch_app_data(app_id, table)

    Return:
        Dictionary
    """
    data = {}
    try:
        if fields_to_pluck:
            data = (
                r
                .table(table)
                .get(app_id)
                .pluck(fields_to_pluck)
                .run(conn)
            )

        else:
            data = (
                r
                .table(table)
                .get(app_id)
                .run(conn)
            )

    except Exception as e:
        logger.exception(e)

    return(data)

@db_create_close
def fetch_app_data_by_appid_and_agentid(
    app_id, agent_id, table=AppCollections.UniqueApplications,
    fields_to_pluck=None, conn=None
    ):
    """Fetch application data by app id
    Args:
        app_id (str): 64 character ID of the application.
        agent_id (str): 36 character UUID of the agent.

    Kwargs:
        table (str): The name of the apps per agent collection,
            that will be used when updating the application data.

    Basic Usage:
        >>> from vFense.plugins.patching._db import fetch_app_data
        >>> app_id = '15fa819554aca425d7f699e81a2097898b06f00a0f2dd6e8d51a18405360a6eb'
        >>> agent_id = '7f242ab8-a9d7-418f-9ce2-7bcba6c2d9dc'
        >>> table = 'unique_applications'
        >>> fetch_app_data_by_agentid(app_id, agent_id, table)

    Return:
        Dictionary
    """

    data = {}
    index_to_use = DbCommonAppPerAgentIndexes.AgentIdAndAppId
    try:
        if fields_to_pluck:
            data = (
                r
                .table(table)
                .get_all([agent_id, app_id], index=index_to_use)
                .pluck(fields_to_pluck)
                .run(conn)
            )
            if data:
                data = data[0]

        else:
            data = (
                r
                .table(table)
                .get_all([agent_id, app_id], index=index_to_use)
                .run(conn)
            )
            if data:
                data = data[0]

    except Exception as e:
        logger.exception(e)

    return(data)


@time_it
@db_create_close
def fetch_app_data_to_send_to_agent(
    app_id, agent_id,
    table=AppCollections.UniqueApplications, conn=None
    ):
    """Fetch application data by app id
    Args:
        app_id (str): 64 character ID of the application.
        agent_id (str): 36 character UUID of the agent.

    Kwargs:
        table (str): The name of the apps per agent collection,
            that will be used when updating the application data.

    Basic Usage:
        >>> from vFense.plugins.patching._db import fetch_app_data
        >>> app_id = 'c726edf62d1d17ca8b420f24bbdc9c8fa58d000b51d31614e3826c2fb37a2929'
        >>> agent_id = '33ba8521-b2e5-47dc-9bdc-0f1e3384049d'
        >>> table = 'unique_applications'
        >>> fetch_app_data_by_agentid(app_id, agent_id, table)

    Return:
        Dictionary
        {
            "file_data": [
                {
                    "file_hash": "47dc1daa42e6d53e1a881f4ed9c5472f6732665af2cba082f8fa3931199fb746", 
                    "file_name": "gpgv_1.4.11-3ubuntu2.5_amd64.deb", 
                    "file_uri": "http://us.archive.ubuntu.com/ubuntu/pool/main/g/gnupg/gpgv_1.4.11-3ubuntu2.5_amd64.deb", 
                    "file_size": 185400
                }
            ], 
            "cli_options": "", 
            "version": "1.4.11-3ubuntu2.5", 
            "name": "gpgv"
        }
    """

    data = {}
    try:
        data = list(
            r
            .table(table)
            .get_all(app_id)
            .map(
                lambda app:
                {
                    DbCommonAppKeys.Name: app[DbCommonAppKeys.Name],
                    DbCommonAppKeys.Version: app[DbCommonAppKeys.Version],
                    DbCommonAppKeys.CliOptions: (
                        r.branch(
                            app.has_fields(DbCommonAppKeys.CliOptions) == False,
                            '',
                            app[DbCommonAppKeys.CliOptions]
                        )
                    ),
                    CommonFileKeys.PKG_FILEDATA: (
                        r
                        .table(FileCollections.Files)
                        .filter(
                            lambda x: (
                                x[FilesKey.AppIds].contains(app_id)
                                &
                                x[FilesKey.AgentIds].contains(agent_id)
                            )
                        )
                        .coerce_to('array')
                        .without(FilesKey.AppIds, FilesKey.AgentIds)
                    )
                }
            )
            .run(conn)
        )
        if data:
            data = data[0]

    except Exception as e:
        logger.exception(e)

    return(data)


@time_it
@db_create_close
def return_valid_appids_for_agent(
    app_ids, agent_id,
    table=AppCollections.AppsPerAgent, conn=None
    ):
    """Return the valid application ids, from the list of application ids
        that were passed into this function
    Args:
        app_ids (list): List of application ids
        agent_id (str): The 36 character UUID of the agent.

    Kwargs:
        table (str): The name of the collection that will be queried.
            default = 'apps_per_agent'

    Basic Usage:
        >>> from vFense.plugins.patching._db import return_valid_appids_for_agent
        >>> app_ids = ['c726edf62d1d17ca8b420f24bbdc9c8fa58d000b51d31614e3826c2fb37a2929', 'foo']
        >>> agent_id = '33ba8521-b2e5-47dc-9bdc-0f1e3384049d'
        >>> table = 'apps_per_agent'
        >>> return_valid_appids_for_agent(app_ids, agent_id, table)

    Returns:
        List
        [
            "c726edf62d1d17ca8b420f24bbdc9c8fa58d000b51d31614e3826c2fb37a2929"
        ]
    """
    data = []
    try:
        data = (
            r
            .expr(app_ids)
            .map(
                lambda app_id:
                r
                .table(table)
                .get_all(
                    [agent_id, app_id],
                    index=DbCommonAppPerAgentIndexes.AgentIdAndAppId
                )
                .coerce_to('array')
            )
            .concat_map(lambda app_id: app_id[DbCommonAppKeys.AppId])
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return(data)


@time_it
@db_create_close
@return_status_tuple
def update_apps_by_customer(
    customer_name, app_data, collection=AppCollections.AppsPerAgent,
    index_name=AppsPerAgentIndexes.CustomerName,
    conn=None):
    """ Update any keys for any apps collection by customer name
        This function should not be called directly.
    Args:
        customer_name (str): Name of the customer.
        app_data (dict): Dictionary of the key and values that you are updating.

    Kwargs:
        collection (str): The Application Collection that is going to be used.
        index_name (str): The name of the index that will be used during the search.

    Basic Usage:
        >>> from vFense.plugins.patching._db import update_app_per_agent_data_by_customer
        >>> customer_name = 'vFense'
        >>> app_data = {'customer_name': 'vFense'} 
        >>> collection = 'apps_per_agent'
        >>> index_name = 'customer_name'
        >>> update_app_per_agent_data_by_customer(customer_name,_app_data, collection, index_name)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """

    data = {}
    try:
        data = (
            r
            .table(collection)
            .get_all(
                customer_name, index=index_name
            )
            .update(app_data)
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return(data)


def update_os_apps_for_agent_by_customer(customer_name, app_data):
    """Update all apps for all agents by customer for 
        the apps_per_agent collection, using the customer_name
        index.
        This function should not be called directly.
    Args:
        customer_name (str): Name of the customer.
        app_data (dict): The data that you are updating.

    Basic Usage:
        >>> from vFense.plugins.patching._db import update_os_apps_for_agent_by_customer
        >>> customer_name = 'vFense'
        >>> app_data = {'customer_name': 'vFense'}
        >>> update_os_apps_for_agent_by_customer(customer_name, app_data)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    collection_name = AppCollections.AppsPerAgent
    index_name = AppsPerAgentIndexes.CustomerName
    return(
        update_apps_by_customer(
            customer_name, app_data,
            collection_name, index_name
        )
    )


def update_supported_apps_for_agent_by_customer(customer_name, app_data):
    """Update all apps for all agents by customer for 
        the supported_apps_per_agent collection, using the customer_name
        index.
        This function should not be called directly.
    Args:
        customer_name (str): Name of the customer.
        app_data (dict): The data that you are updating.

    Basic Usage:
        >>> from vFense.plugins.patching._db import update_supported_apps_for_agent_by_customer
        >>> customer_name = 'vFense'
        >>> app_data = {'customer_name': 'vFense'}
        >>> update_supported_apps_for_agent_by_customer(customer_name, app_data)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    collection_name = AppCollections.SupportedAppsPerAgent
    index_name = SupportedAppsPerAgentIndexes.CustomerName
    return(
        update_apps_by_customer(
            customer_name, app_data,
            collection_name, index_name
        )
    )


def update_custom_apps_for_agent_by_customer(customer_name, app_data):
    """Update all apps for all agents by customer for 
        the custom_apps_per_agent collection, using the customer_name
        index.
        This function should not be called directly.
    Args:
        customer_name (str): Name of the customer.
        app_data (dict): The data that you are updating.

    Basic Usage:
        >>> from vFense.plugins.patching._db import update_custom_apps_for_agent_by_customer
        >>> customer_name = 'vFense'
        >>> app_data = {'customer_name': 'vFense'}
        >>> update_custom_apps_for_agent_by_customer(customer_name, app_data)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    collection_name = AppCollections.CustomAppsPerAgent
    index_name = CustomAppsPerAgentIndexes.CustomerName
    return(
        update_apps_by_customer(
            customer_name, app_data,
            collection_name, index_name
        )
    )


def update_agent_apps_for_agent_by_customer(customer_name, app_data):
    """Update all apps for all agents by customer for 
        the agent_apps_per_agent collection, using the customer_name
        index.
        This function should not be called directly.
    Args:
        customer_name (str): Name of the customer.
        app_data (dict): The data that you are updating.

    Basic Usage:
        >>> from vFense.plugins.patching._db import update_agent_apps_for_agent_by_customer
        >>> customer_name = 'vFense'
        >>> app_data = {'customer_name': 'vFense'}
        >>> update_agent_apps_for_agent_by_customer(customer_name, app_data)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    collection_name = AppCollections.CustomAppsPerAgent
    index_name = CustomAppsPerAgentIndexes.CustomerName
    return(
        update_apps_by_customer(
            customer_name, app_data,
            collection_name, index_name
        )
    )


@time_it
@db_create_close
@return_status_tuple
def delete_apps_by_customer(
    customer_name, collection=AppCollections.AppsPerAgent,
    index_name=AppsPerAgentIndexes.CustomerName,
    conn=None):
    """Delete all apps for all agents by customer and app type
        This function should not be called directly.
    Args:
        customer_name (str): Name of the customer.

    Kwargs:
        collection (str): The Application Collection that is going to be used.
        index_name (str): The name of the index that will be used during the search.

    Basic Usage:
        >>> from vFense.plugins.patching._db import delete_apps_by_customer
        >>> customer_name = 'vFense'
        >>> collection = 'apps_per_agent'
        >>> index_name = 'customer_name'
        >>> delete_apps_by_customer(customer_name,_collection, index_name)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """

    data = {}
    try:
        data = (
            r
            .table(collection)
            .get_all(
                customer_name, index=index_name
            )
            .delete()
            .run(conn)
        )
    except Exception as e:
        logger.exception(e)

    return(data)


def delete_os_apps_for_agent_by_customer(customer_name):
    collection_name = AppCollections.AppsPerAgent
    index_name = AppsPerAgentIndexes.CustomerName
    """Delete all apps for all agents by customer for 
        the apps_per_agent collection, using the customer_name
        index.
        This function should not be called directly.
    Args:
        customer_name (str): Name of the customer.

    Basic Usage:
        >>> from vFense.plugins.patching._db import delete_os_apps_for_agent_by_customer
        >>> customer_name = 'vFense'
        >>> delete_os_apps_for_agent_by_customer(customer_name)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    return(
        delete_apps_by_customer(
            customer_name,
            collection_name,
            index_name
        )
    )


def delete_supported_apps_for_agent_by_customer(customer_name):
    collection_name = AppCollections.SupportedAppsPerAgent
    index_name = SupportedAppsPerAgentIndexes.CustomerName
    """Delete all apps for all agents by customer for 
        the supported_apps_per_agent collection, using the customer_name
        index.
        This function should not be called directly.
    Args:
        customer_name (str): Name of the customer.

    Basic Usage:
        >>> from vFense.plugins.patching._db import delete_supported_apps_for_agent_by_customer
        >>> customer_name = 'vFense'
        >>> delete_supported_apps_for_agent_by_customer(customer_name)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    return(
        delete_apps_by_customer(
            customer_name,
            collection_name,
            index_name
        )
    )


def delete_custom_apps_for_agent_by_customer(customer_name):
    collection_name = AppCollections.CustomAppsPerAgent
    index_name = CustomAppsPerAgentIndexes.CustomerName
    """Delete all apps for all agents by customer for 
        the custom_apps_per_agent collection, using the customer_name
        index.
        This function should not be called directly.
    Args:
        customer_name (str): Name of the customer.

    Basic Usage:
        >>> from vFense.plugins.patching._db import delete_custom_apps_for_agent_by_customer
        >>> customer_name = 'vFense'
        >>> delete_custom_apps_for_agent_by_customer(customer_name)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    return(
        delete_apps_by_customer(
            customer_name,
            collection_name,
            index_name
        )
    )


def delete_agent_apps_for_agent_by_customer(customer_name):
    collection_name = AppCollections.AgentAppsPerAgent
    index_name = AgentAppsPerAgentIndexes.CustomerName
    """Delete all apps for all agents by customer for 
        the agent_apps_per_agent collection, using the customer_name
        index.
        This function should not be called directly.
    Args:
        customer_name (str): Name of the customer.

    Basic Usage:
        >>> from vFense.plugins.patching._db import delete_agent_apps_for_agent_by_customer
        >>> customer_name = 'vFense'
        >>> delete_agent_apps_for_agent_by_customer(customer_name)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    return(
        delete_apps_by_customer(
            customer_name,
            collection_name,
            index_name
        )
    )

@time_it
@db_create_close
@return_status_tuple
def update_app_data_for_agent(
    agent_id, app_id, data,
    table=AppCollections.AppsPerAgent,
    index_to_use=AppsPerAgentIndexes.AgentIdAndAppId,
    conn=None
    ):
    """Update app data for an agent.
        This function should not be called directly.
    Args:
        agent_id (str): 36 character UUID of the agent.
        app_id (str): 64 character ID of the application.
        data(dict): Dictionary of the application data that
            is being updated for the agent.
    Kwargs:
        table (str): The name of the apps per agent collection,
            that will be used when updating the application data.
        index_to_use (str): The secondary index, that will be used when searching
            for the app_id and agent_id.

    Basic Usage:
        >>> from vFense.plugins.patching._db import update_app_data_for_agent
        >>> agent_id = '7f242ab8-a9d7-418f-9ce2-7bcba6c2d9dc'
        >>> app_id = '15fa819554aca425d7f699e81a2097898b06f00a0f2dd6e8d51a18405360a6eb'
        >>> data = {'status': 'pending'}
        >>> table = 'apps_per_agent'
        >>> index = 'agentid_and_appid'
        >>> update_app_data_for_agent(agent_id, app_id, data, table, index)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .table(table)
            .get_all([object_id, app_id], index=index_to_use)
            .update(data)
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return(data)

@time_it
def update_os_app_data_for_agent(agent_id, app_id, data):
    """Update the apps_per_agent collection by agent_id and app_id.
        This function should not be called directly.
    Args:
        agent_id (str): 36 character UUID of the agent.
        app_id (str): 64 character ID of the application.
        data(dict): Dictionary of the application data that
            is being updated for the agent.

    Basic Usage:
        >>> from vFense.plugins.patching._db import update_os_app_data_for_agent
        >>> agent_id = '7f242ab8-a9d7-418f-9ce2-7bcba6c2d9dc'
        >>> app_id = '15fa819554aca425d7f699e81a2097898b06f00a0f2dd6e8d51a18405360a6eb'
        >>> data = {'status': 'pending'}
        >>> update_os_app_data_for_agent(agent_id, app_id, data)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    table = AppCollections.AppsPerAgent
    index = AppsPerAgentIndexes.AgentIdAndAppId
    return(
        update_app_data_for_agent(
            agent_id, app_id, data,
            table=table, index_to_use=index
        )
    )
 
@time_it
def update_custom_app_data_for_agent(agent_id, app_id, data):
    """Update the custom_apps_per_agent collection by agent_id and app_id.
        This function should not be called directly.
    Args:
        agent_id (str): 36 character UUID of the agent.
        app_id (str): 64 character ID of the application.
        data(dict): Dictionary of the application data that
            is being updated for the agent.

    Basic Usage:
        >>> from vFense.plugins.patching._db import update_custom_app_data_for_agent
        >>> agent_id = '7f242ab8-a9d7-418f-9ce2-7bcba6c2d9dc'
        >>> app_id = '15fa819554aca425d7f699e81a2097898b06f00a0f2dd6e8d51a18405360a6eb'
        >>> data = {'status': 'pending'}
        >>> update_custom_app_data_for_agent(agent_id, app_id, data)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    table = AppCollections.CustomAppsPerAgent
    index = CustomAppsPerAgentIndexes.AgentIdAndAppId
    return(
        update_app_data_for_agent(
            agent_id, app_id, data,
            table=table, index_to_use=index
        )
    )

@time_it
def update_vfense_app_data_for_agent(agent_id, app_id, data):
    """Update the vfense_apps_per_agent collection by agent_id and app_id.
        This function should not be called directly.
    Args:
        agent_id (str): 36 character UUID of the agent.
        app_id (str): 64 character ID of the application.
        data(dict): Dictionary of the application data that
            is being updated for the agent.

    Basic Usage:
        >>> from vFense.plugins.patching._db import update_vfense_app_data_for_agent
        >>> agent_id = '7f242ab8-a9d7-418f-9ce2-7bcba6c2d9dc'
        >>> app_id = '15fa819554aca425d7f699e81a2097898b06f00a0f2dd6e8d51a18405360a6eb'
        >>> data = {'status': 'pending'}
        >>> update_vfense_app_data_for_agent(agent_id, app_id, data)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    table = AppCollections.vFenseAppsPerAgent
    index = vFenseAppsPerAgent.AgentIdAndAppId
    return(
        update_app_data_for_agent(
            agent_id, app_id, data,
            table=table, index_to_use=index
        )
    )
 
