import os
import logging

from vFense.core._constants import *
from vFense.operations._constants import AgentOperations
from vFense.errorz.status_codes import DbCodes
from vFense.plugins.patching._constants import CommonAppKeys, \
    FileLocationUris, CommonFileKeys
from vFense.core.decorators import time_it 
from vFense.core.customer import CustomerKeys
from vFense.core.customer.customers import get_customer_property
from vFense.plugins.patching._db import delete_os_apps_for_agent_by_customer, \
    delete_supported_apps_for_agent_by_customer, \
    delete_custom_apps_for_agent_by_customer, \
    delete_agent_apps_for_agent_by_customer, \
    update_os_apps_for_agent_by_customer, \
    update_supported_apps_for_agent_by_customer, \
    update_custom_apps_for_agent_by_customer, \
    update_agent_apps_for_agent_by_customer, \
    fetch_file_servers_addresses

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')


def get_base_url(customer_name):
    return (get_customer_property(customer_name, CustomerKeys.PackageUrl))

def get_download_urls(customer_name, app_id, file_data):
    """Replace the vendor supplied url with the vFense Server urls
    Args:
        customer_name (str): The name of the customer
        app_id (str): The 64 character ID of the app
        file_data (list): List of the file_data that will be manipulated

    Basic Usage:
        >>> from vFense.plugins.patching._db import fetch_file_data
        >>> from vFense.plugins.patching.patching import get_download_urls
        >>> customer_name = 'default'
        >>> app_id = 'c726edf62d1d17ca8b420f24bbdc9c8fa58d000b51d31614e3826c2fb37a2929'
        >>> file_data = fetch_file_data(app_id)
        >>> get_download_urls(customer_name, app_id, file_data)

    Returns:
        List of dictionaries
        [
            {
                "file_uris": [
                    "https://10.0.0.15/packages/c726edf62d1d17ca8b420f24bbdc9c8fa58d000b51d31614e3826c2fb37a2929gpgv_1.4.11-3ubuntu2.5_amd64.deb"
                ], 
                "file_name": "gpgv_1.4.11-3ubuntu2.5_amd64.deb", 
                "file_hash": "47dc1daa42e6d53e1a881f4ed9c5472f6732665af2cba082f8fa3931199fb746", 
                "file_size": 185400, 
                "file_uri": "https://10.0.0.15/packages/c726edf62d1d17ca8b420f24bbdc9c8fa58d000b51d31614e3826c2fb37a2929/gpgv_1.4.11-3ubuntu2.5_amd64.deb"
            }
        ]
    """
    uris = []
    url_base = get_base_url(customer_name)
    file_uris_base = None
    url_base = os.path.join(url_base,app_id)
    file_uris_base = os.path.join(FileLocationUris.PACKAGES, app_id)

    for pkg in file_data:
        file_servers = fetch_file_servers_addresses(customer_name)
        file_uris = []
        if file_servers:
            for mm in file_servers:
                file_uris.append(
                    'http://%s/%s%s' %
                    (mm[FileServerKeys.Addresses], file_uris_base, pkg[CommonFileKeys.PKG_NAME])
                )
        file_uris.append(url_base + pkg[CommonFileKeys.PKG_NAME])
        uris.append(
            {
                CommonFileKeys.PKG_NAME: pkg[CommonFileKeys.PKG_NAME],
                CommonFileKeys.PKG_URI: os.path.join(url_base, pkg[CommonFileKeys.PKG_NAME]),
                CommonFileKeys.FILE_URIS: file_uris,
                CommonFileKeys.PKG_SIZE: pkg[CommonFileKeys.PKG_SIZE],
                CommonFileKeys.PKG_HASH: pkg[CommonFileKeys.PKG_HASH]
            }
        )

    return(uris)


@time_it
def remove_all_apps_for_customer(customer_name):
    delete_os_apps_for_agent_by_customer(customer_name)
    delete_supported_apps_for_agent_by_customer(customer_name)
    delete_custom_apps_for_agent_by_customer(customer_name)
    delete_agent_apps_for_agent_by_customer(customer_name)


@time_it
def update_all_apps_for_customer(customer_name):
    app_data = {CommonAppKeys.CustomerName: customer_name}
    update_os_apps_for_agent_by_customer(customer_name, app_data)
    update_supported_apps_for_agent_by_customer(customer_name, app_data)
    update_custom_apps_for_agent_by_customer(customer_name, app_data)
    update_agent_apps_for_agent_by_customer(customer_name, app_data)


@time_it
def update_app_status_by_agentid_and_appid(
    agent_id, app_id, status=CommonAppKeys.PENDING
    ):
    """Update the application status for an agent
    Args:
        agent_id (str): 36 character UUID of the agent.
        app_id (str): 64 character ID of the application.

    Basic Usage:
        >>> from vFense.plugins.patching.patching import update_app_status_by_agentid_and_appid
        >>> agent_id = '7f242ab8-a9d7-418f-9ce2-7bcba6c2d9dc'
        >>> app_id = '15fa819554aca425d7f699e81a2097898b06f00a0f2dd6e8d51a18405360a6eb'
        >>> status = 'pending'
        >>> update_app_status_by_agentid_and_appid(agent_id, app_id, status)

    Returns:
        Boolean
    """
    updated = False
    if status in CommonAppKeys.ValidPackageStatuses:
        status_code, count, error, generated_ids = (
            update_os_app_data_for_agent(
                agent_id, app_id, status
            )
        )
        if status_code != DbCodes.Replaced and count < 1:
            status_code, count, error, generated_ids = (
                update_custom_app_data_for_agent(
                    agent_id, app_id, status
                )
            )
            if status_code != DbCodes.Replaced and count < 1:
                status_code, count, error, generated_ids = (
                    update_supported_app_data_for_agent(
                        agent_id, app_id, status
                    )
                )
                if status_code != DbCodes.Replaced and count < 1:
                    status_code, count, error, generated_ids = (
                        update_vfense_app_data_for_agent(
                            agent_id, app_id, status
                        )
                    )
    return(updated)
