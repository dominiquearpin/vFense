from vFense.core.agent import *
import logging
import logging.config
from vFense.utils.common import *
from vFense.core.agent.agents import *
from vFense.plugins.patching import * 
from time import ctime
from vFense.core.tag.tagManager import get_agent_ids_from_tag

from vFense.db.client import db_create_close, r
from vFense.plugins.patching.rv_db_calls import get_all_app_stats_by_agentid
from vFense.errorz.error_messages import GenericResults

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')


def get_agentids(os_code=None, customer_name=None, tag_id=None):
    agentids=[]
    agent_ids_for_tag_id= get_agent_ids_from_tag(tag_id=tag_id)
    agent_ids_for_os_customer=get_all_agent_ids(agent_os=os_code,customer_name=customer_name)
    agentids=list(set(agent_ids_for_tag_id + agent_ids_for_os_customer))
    return(agentids)


@db_create_close
def get_all_agentids(username, customer_name, count=30, offset=0, 
        uri=None, method=None, conn=None):

    try:
        count = (
                r
                .table(AgentsCollection)
                .get_all(customer_name, index=AgentKey.CustomerName)
                .count()
                .run(conn)
                )

        data = list(
                r
                .table(AgentsCollection)
                .get_all(customer_name, index=AgentKey.CustomerName)
                .pluck(AgentKey.AgentId)
                .order_by(AgentKey.ComputerName)
                .skip(offset)
                .limit(count)
                .run(conn)
            )

        if data:
            print data
            for agent in data:
                agent[BASIC_RV_STATS] = (
                        get_all_app_stats_by_agentid(
                            username, customer_name,
                            uri,  method, agent[AgentKey.AgentId]
                            )['data']
                        )
        status = (
                GenericResults(
                    username,  uri, method
                    ).information_retrieved(data, count)
                )
        logger.info(status['message'])
    
    except Exception as e:
        status = (
                GenericResults(
                    username,  uri, method
                    ).something_broke('get_all_agents', 'agent', e)
                )
        return(status)

def system_os_details(agent_info):
    if agent_info:
        data={
                "computer-name":agent_info.get(AgentKey.ComputerName),
                "os-type":agent_info.get(AgentKey.OsCode), 
                "os-name":agent_info.get(AgentKey.OsString),
                "system-arch":agent_info.get('bit_type'),
                "machine-type":agent_info.get(AgentKey.MachineType),
                }
        return(data)


def system_hardware_details(agent_info):
    if agent_info:
        hardware_info=agent_info.get(AgentKey.Hardware)
        data={
                "computer-name":agent_info.get(AgentKey.ComputerName),  
                "cpu":hardware_info.get('cpu'), 
                "disk":hardware_info.get('storage'), 
                "display":hardware_info.get('display'), 
                "ram":hardware_info.get('memory'), 
                } 
        return(data)


def system_network_details(agent_info):
    if agent_info:
        hardware_info=agent_info.get(AgentKey.Hardware)
        data={
                "computer-name":agent_info.get(AgentKey.ComputerName),
                "network":hardware_info.get('nic'),
                }
        return(data)


def system_cpu_stats(agent_info):
    if agent_info:
        monit_stats=agent_info.get('monit_stats')
        if monit_stats:
            cpu_stats=monit_stats.get('cpu')
            data = {
                    "computer-name": agent_info.get(AgentKey.ComputerName),
                    "last-updated-at":time.ctime(monit_stats['timestamp']),
                    "idle":cpu_stats.get('idle'),
                    "user":cpu_stats.get('user'),
                    "system":cpu_stats.get('system'),
                    }
            return(data)


def system_memory_stats(agent_info):
    if agent_info:
        monit_stats=agent_info.get('monit_stats')
        if monit_stats:
            memory_stats=monit_stats.get('memory')
            data = {
                    "computer-name": agent_info.get(AgentKey.ComputerName),
                    "last-updated-at":time.ctime(monit_stats['timestamp']),
                    "total":memory_stats.get('total'),
                    "used":memory_stats.get('used'),
                    "used-percentage":memory_stats.get('used_percent'),
                    "free":memory_stats.get('free'),
                    "free-percent":memory_stats.get('free_percent'),
                    }
            return(data)


def system_disk_stats(agent_info):
    if agent_info:
        monit_stats=agent_info.get('monit_stats')
        if monit_stats:
            file_system=monit_stats.get('file_system')
            if file_system:
                data ={
                        "computer-name": agent_info.get(AgentKey.ComputerName),
                        "disk-usage":file_system,
                        }
                return(data)

def agent_last_updated(agent_info):
    if agent_info:
        last_updated= agent_info.get('last_agent_update')
        data = {
                "computer-name": agent_info.get(AgentKey.ComputerName),
                "last_agent_update": last_updated.strftime("%b %d %Y %H:%M:%S"),
                }
        return (data)

def agent_status(agent_info):
    if agent_info:
        agent_status = agent_info.get('agent_status')
        return(agent_status)


def systems_os_details(username, customer_name, os_code=None, 
        tag_id=None, uri=None, method=None):
    systems_os_details=[]
    agentids=get_agentids(os_code=os_code, customer_name=customer_name, tag_id=tag_id)
    for agentid in agentids:
        agent_info=get_agent_info(agent_id=agentid)
        system_detail=system_os_details(agent_info=agent_info)
        if system_detail:
            systems_os_details.append(system_detail)

    try:
        data = systems_os_details
        results = (
                GenericResults(
                    username, uri, method,
                    ).information_retrieved(data, len(data))
                )
    
    except Exception as e:
        logger.exception(e)
        results = (
                GenericResults(
                    username, uri, method
                    ).something_broke('Systems_os_details', 'failed to retrieve data', e)
                )
    return(results)


def systems_hardware_details (username, customer_name, os_code=None, 
        tag_id=None, uri=None, method=None):
    systems_hardware_details=[]
    agentids=get_agentids(os_code=os_code, customer_name=customer_name, tag_id=tag_id)
    for agentid in agentids:
        agent_info=get_agent_info(agent_id=agentid)
        hardware_details=system_hardware_details(agent_info=agent_info)
        if hardware_details:
            systems_hardware_details.append(hardware_details)

    try:
        data = systems_hardware_details
        results = (
                GenericResults(
                    username, uri, method,
                    ).information_retrieved(data, len(data))
                )
    
    except Exception as e:
        logger.exception(e)
        results = (
                GenericResults(
                    username, uri, method
                    ).something_broke('Systems_hardware_details', 'failed to retrieve data', e)
                )
    return(results)


def systems_cpu_details (username, customer_name, os_code=None, 
        tag_id=None, uri=None, method=None):
    systems_cpu_details=[]
    agentids=get_agentids(os_code=os_code, customer_name=customer_name, tag_id=tag_id)
    for agentid in agentids:
        agent_info=get_agent_info(agent_id=agentid)
        cpu_stats=system_cpu_stats(agent_info)
        if cpu_stats:
            systems_cpu_details.append(cpu_stats)
    
    try:
        data = systems_cpu_details
        results = (
                GenericResults(
                    username, uri, method,
                    ).information_retrieved(data, len(data))
                )
    
    except Exception as e:
        logger.exception(e)
        results = (
                GenericResults(
                    username, uri, method
                    ).something_broke('Systems_cpu_details', 'failed to retrieve data', e)
                )
    return(results)

def systems_memory_stats(username, customer_name, os_code=None, 
        tag_id=None, uri=None, method=None):
    systems_memory_details=[]
    agentids=get_agentids(os_code=os_code, customer_name=customer_name, tag_id=tag_id)
    for agentid in agentids:
        agent_info=get_agent_info(agent_id=agentid)
        memory_stats=system_memory_stats(agent_info)
        if memory_stats:
            systems_memory_details.append(memory_stats)
    
    try:
        data = systems_memory_details
        results = (
                GenericResults(
                    username, uri, method,
                    ).information_retrieved(data, len(data))
                )
    
    except Exception as e:
        logger.exception(e)
        results = (
                GenericResults(
                    username, uri, method
                    ).something_broke('Systems_os_details', 'failed to retrieve data', e)
                )
    return(results)


def systems_disk_stats(username, customer_name, os_code=None, 
        tag_id=None, uri=None, method=None):
    systems_disk_details=[]
    agentids=get_agentids(os_code=os_code, customer_name=customer_name, tag_id=tag_id)
    for agentid in agentids:
        agent_info=get_agent_info(agent_id=agentid)
        disk_stats=system_disk_stats(agent_info)
        if disk_stats:
            systems_disk_details.append(disk_stats)
    
    try:
        data = systems_disk_details
        results = (
                GenericResults(
                    username, uri, method,
                    ).information_retrieved(data, len(data))
                )
    
    except Exception as e:
        logger.exception(e)
        results = (
                GenericResults(
                    username, uri, method
                    ).something_broke('Systems_os_details', 'failed to retrieve data', e)
                )
    return(results)

def systems_network_details(username, customer_name, os_code=None, 
        tag_id=None, uri=None, method=None):
    systems_network_infos=[]
    agentids=get_agentids(os_code=os_code, customer_name=customer_name, tag_id=tag_id)
    for agentid in agentids:
        agent_info=get_agent_info(agent_id=agentid)
        network_details=system_network_details(agent_info)
        if network_details:
            systems_network_infos.append(network_details)
    
    try:
        data = systems_network_infos
        results = (
                GenericResults(
                    username, uri, method,
                    ).information_retrieved(data, len(data))
                )
    
    except Exception as e:
        logger.exception(e)
        results = (
                GenericResults(
                    username, uri, method
                    ).something_broke('Systems_os_details', 'failed to retrieve data', e)
                )
    return(results)

def agents_last_updated(username, customer_name, os_code=None, 
        tag_id=None, uri=None, method=None):
    agents_uptime_info=[]
    agentids=get_agentids(os_code=os_code, customer_name=customer_name, tag_id=tag_id)
    for agentid in agentids:
        agent_info=get_agent_info(agent_id=agentid)
        last_updated=agent_last_updated(agent_info)
        if last_updated:
            agents_uptime_info.append(last_updated)
    
    try:
        data = agents_uptime_info
        results = (
                GenericResults(
                    username, uri, method,
                    ).information_retrieved(data, len(data))
                )
    
    except Exception as e:
        logger.exception(e)
        results = (
                GenericResults(
                    username, uri, method
                    ).something_broke('Systems_os_details', 'failed to retrieve data', e)
                )
    return(results)

def agents_reboot_pending(username, customer_name, os_code=None, 
        tag_id=None, uri=None, method=None):
    agents_need_reboot = []
    agents_not_need_reboot =[]
    agentids=get_agentids(os_code=os_code, customer_name=customer_name, tag_id=tag_id)
    for agentid in agentids:
        agent_info=get_agent_info(agent_id=agentid)
        if agent_info:
            computer_name = agent_info.get('computer_name')
            needs_reboot= agent_info.get('needs_reboot')
            if needs_reboot == 'yes':
                agents_need_reboot.append(computer_name)
            elif needs_reboot == 'no' :
                agents_not_need_reboot.append(computer_name)
    data = {
            'reboot_required': agents_need_reboot,
            'reboot_not_required': agents_not_need_reboot,
            }
    
    try:
        data = data
        results = (
                GenericResults(
                    username, uri, method,
                    ).information_retrieved(data, len(data))
                )
    
    except Exception as e:
        logger.exception(e)
        results = (
                GenericResults(
                    username, uri, method
                    ).something_broke('Systems_os_details', 'failed to retrieve data', e)
                )
    return(results)

def agents_status(username, customer_name, os_code=None, 
        tag_id=None, uri=None, method=None):
    nodes_status=[]
    agents_up = []
    agents_down = [] 
    agentids=get_agentids(os_code=os_code, customer_name=customer_name, tag_id=tag_id)
    for agentid in agentids:
        agent_info=get_agent_info(agent_id=agentid)
        computer_name = agent_info.get('computer_name')
        node_status=agent_status(agent_info)
        if node_status == 'down':
            agents_down.append(computer_name)
        elif node_status == 'up':
            agents_up.append(computer_name)
    data = {
            'agents_up':agents_up,
            'agents_down':agents_down,
            }
    
    try:
        data = data
        results = (
                GenericResults(
                    username, uri, method,
                    ).information_retrieved(data, len(data))
                )
    
    except Exception as e:
        logger.exception(e)
        results = (
                GenericResults(
                    username, uri, method
                    ).something_broke('Systems_os_details', 'failed to retrieve data', e)
                )
    return(results)

