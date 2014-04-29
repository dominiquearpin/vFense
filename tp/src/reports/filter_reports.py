import logging
import logging.config

from vFense.core.agent import *
from vFense.utils.common import *
from vFense.core.agent.agents import *
from vFense.plugins.patching import * 
from time import ctime
from vFense.core.tag.tagManager import get_agent_ids_from_tag

from vFense.db.client import db_create_close, r
from vFense.plugins.patching.rv_db_calls import get_all_app_stats_by_agentid
from vFense.plugins.patching._constants import *
from vFense.errorz.error_messages import GenericResults

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')


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
            #for agent in data:
            #    agent[BASIC_RV_STATS] = (
            #            get_all_app_stats_by_agentid(
            #                username, customer_name,
            #                uri,  method, agent[AgentKey.AgentId]
            #                )['data']
            #            )
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


@db_create_close
def filter_by_and_query(username, customer_name, keys_to_pluck, key = AgentKey.ComputerName,
        count=30, offset=0, query=None, uri=None, method=None, conn=None):
    
    print key
    print query
    if query:
        count = (
                r
               .table(AgentsCollection)
               .get_all(customer_name, index=AgentKey.CustomerName)
               .filter(
                   (r.row[AgentKey.ComputerName].match("(?i)"+query))
                   )
               .count()
               .run(conn)
               )

        data = list(
                r
                .table(AgentsCollection)
                .get_all(customer_name, index=AgentKey.CustomerName)
                .filter(
                    (r.row[key].match("(?i)"+query))
                    )
                .pluck(keys_to_pluck)
                .skip(offset)
                .limit(count)
                .run(conn)
                )
    else:
        
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
                .pluck(keys_to_pluck)
                .skip(offset)
                .limit(count)
                .run(conn)
                )
    return(data)



def systems_os_details(username, customer_name, key, query, uri=None, method=None):
   
    keys_to_pluck = [AgentKey.ComputerName, AgentKey.OsCode, 
            AgentKey.OsString, AgentKey.MachineType, AgentKey.SysArch]
    
    data = filter_by_and_query(username=username, customer_name=customer_name,
            key=key, query=query,keys_to_pluck=keys_to_pluck)

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

def systems_hardware_details (username, customer_name, key, query,  uri=None, method=None):

    keys_to_pluck = [AgentKey.ComputerName, AgentKey.Hardware]
    
    data = filter_by_and_query(username=username, customer_name=customer_name,
            key=key, query=query,keys_to_pluck=keys_to_pluck)

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


def systems_network_details(username, customer_name, key, query,
        uri=None, method=None):

    network_stats=[]
    keys_to_pluck = [AgentKey.ComputerName, AgentKey.Hardware]
    
    data = filter_by_and_query(username=username, customer_name=customer_name,
            key=key, query=query,keys_to_pluck=keys_to_pluck)

    for d in data:
        network_data= {
                "computer_name" : d[AgentKey.ComputerName],
                "network" : d['hardware']['nic']
                }
        network_stats.append(network_data)
    
    try:
        data = network_stats
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


def systems_cpu_details (username, customer_name, key, query, 
        uri=None, method=None):
    
    cpu_stats=[]

    keys_to_pluck = [AgentKey.ComputerName, AgentKey.MonitStats,]
    
    data = filter_by_and_query(username=username, customer_name=customer_name,
            key=key, query=query,keys_to_pluck=keys_to_pluck)
    for d in data:
        cpu_data = {
                "computer-name" : d[AgentKey.ComputerName],
                "last-updated-at": time.ctime(d[AgentKey.MonitStats]['timestamp']),
                "idle": d[AgentKey.MonitStats]['cpu']['idle'],
                "user":d[AgentKey.MonitStats]['cpu']['user'],
                "system":d[AgentKey.MonitStats]['cpu']['system']
                }
        cpu_stats.append(cpu_data)

    try:
        data = cpu_stats
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
            

def systems_memory_stats(username, customer_name, key, query, 
        uri=None, method=None):

    memory_stats = []

    keys_to_pluck = [AgentKey.ComputerName, AgentKey.MonitStats,]
    
    data = filter_by_and_query(username=username, customer_name=customer_name,
            key=key, query=query, keys_to_pluck=keys_to_pluck)
    for d in data:
        memory_data = {
                "computer-name": d[AgentKey.ComputerName],
                "last-updated-at": time.ctime(d[AgentKey.MonitStats]['timestamp']),
                "total" : d[AgentKey.MonitStats]['memory']['total'],
                "used" : d[AgentKey.MonitStats]['memory']['used'],
                "used-percentage": d[AgentKey.MonitStats]['memory']['used_percent'],
                "free":d[AgentKey.MonitStats]['memory']['free'],
                "free-percent": d[AgentKey.MonitStats]['memory']['free_percent'],
                }
        memory_stats.append(memory_data)

    try:
        data = memory_stats
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


def systems_disk_stats(username, customer_name, key, query, 
        uri=None, method=None):
    fs_stats =[]

    keys_to_pluck = [AgentKey.ComputerName, AgentKey.MonitStats,]
    
    data = filter_by_and_query(username=username, customer_name=customer_name,
            key=key, query=query,keys_to_pluck=keys_to_pluck)

    for d in data:
        fs_data = {
                "computer-name": d[AgentKey.ComputerName],
                "disk-usage": d[AgentKey.MonitStats]['file_system'],
                }
        fs_stats.append(fs_data)
    
    try:
        data = fs_stats
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

def agents_last_updated(username, customer_name, agent_os=None, 
        tag_id=None, uri=None, method=None):

    agents_uptime_info=[]
    #agentids=get_agentids(os_code=os_code, customer_name=customer_name, tag_id=tag_id)
    agentids = get_all_agent_ids(customer_name=customer_name, agent_os=agent_os)
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
        agent_info=get_agent_info(agentid=agentid)
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
        agent_info=get_agent_info(agentid=agentid)
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

