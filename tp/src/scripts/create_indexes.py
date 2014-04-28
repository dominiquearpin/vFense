#!/usr/bin/env python

from vFense.db.client import db_connect, r

from vFense.core.agent import *
from vFense.core.tag import *
from vFense.core.user import *
from vFense.core.group import *
from vFense.core.customer import *

from vFense.notifications import *
from vFense.operations import *
from vFense.plugins.patching import *
from vFense.plugins.mightymouse import *
from vFense.plugins.vuln.cve import *
from vFense.plugins.vuln.ubuntu import *
from vFense.plugins.vuln.windows import *
from vFense.core.queue import *

Id = 'id'
def initialize_indexes_and_create_tables():
    tables = [
        ('acls', Id),
        (AgentsCollection, AgentKey.AgentId),
        (AppCollections.UniqueApplications, AppsKey.AppId),
        (AppCollections.AppsPerAgent, Id),
        (AppCollections.CustomApps, CustomAppsKey.AppId),
        (AppCollections.CustomAppsPerAgent, Id),
        (AppCollections.SupportedApps, SupportedAppsKey.AppId),
        (AppCollections.SupportedAppsPerAgent, Id),
        (AppCollections.vFenseApps, vFenseAppsKey.AppId),
        (AppCollections.vFenseAppsPerAgent, Id),
        (FileCollections.Files, FilesKey.FileName),
        (FileCollections.FileServers, FileServerKeys.FileServerName),
        (CVECollections.CVE, CveKey.CveId),
        (WindowsSecurityCollection.Bulletin, WindowsSecurityBulletinKey.Id),
        (UbuntuSecurityCollection.Bulletin, UbuntuSecurityBulletinKey.Id),
        ('downloaded_status', Id),
        (HardwarePerAgentCollection, Id),
        (NotificationCollections.NotificationPlugins, Id),
        (NotificationCollections.Notifications, NotificationKeys.NotificationId),
        (NotificationCollections.NotificationsHistory, Id),
        ('notification_queue', Id),
        (OperationCollections.Agent, AgentOperationKey.OperationId),
        (OperationCollections.Admin, AgentOperationKey.OperationId),
        (OperationCollections.OperationPerAgent, Id),
        (OperationCollections.OperationPerApp, Id),
        ('plugin_configurations', 'name'),
        (DownloadCollections.LatestDownloadedSupported, SupportedAppsKey.AppId),
        (DownloadCollections.LatestDownloadedAgent, SupportedAppsKey.AppId),
        (TagsCollection, TagsKey.TagId),
        (TagsPerAgentCollection, Id),
        (QueueCollections.Agent, Id),
        (UserCollections.Users, UserKeys.UserName),
        (GroupCollections.Groups, GroupKeys.GroupId),
        (GroupCollections.GroupsPerUser, GroupsPerUserKeys.Id),
        (CustomerCollections.Customers, CustomerKeys.CustomerName),
        (CustomerCollections.CustomersPerUser, CustomerPerUserKeys.Id),
    ]
    conn = db_connect()
#################################### If Collections do not exist, create them #########################
    list_of_current_tables = r.table_list().run(conn)
    for table in tables:
        if table[0] not in list_of_current_tables:
            r.table_create(table[0], primary_key=table[1]).run(conn)

#################################### Get All Indexes ###################################################
    app_list = r.table(AppCollections.AppsPerAgent).index_list().run(conn)
    unique_app_list = r.table(AppCollections.UniqueApplications).index_list().run(conn)
    downloaded_list = r.table('downloaded_status').index_list().run(conn)
    custom_app_list = r.table(AppCollections.CustomApps).index_list().run(conn)
    custom_app_per_agent_list = r.table(AppCollections.CustomAppsPerAgent).index_list().run(conn)
    supported_app_list = r.table(AppCollections.SupportedApps).index_list().run(conn)
    supported_app_per_agent_list = r.table(AppCollections.SupportedAppsPerAgent).index_list().run(conn)
    vfense_app_list = r.table(AppCollections.vFenseApps).index_list().run(conn)
    vfense_app_per_agent_list = r.table(AppCollections.vFenseAppsPerAgent).index_list().run(conn)
    cve_list = r.table(CVECollections.CVE).index_list().run(conn)
    windows_bulletin_list = r.table(WindowsSecurityCollection.Bulletin).index_list().run(conn)
    ubuntu_bulletin_list = r.table(UbuntuSecurityCollection.Bulletin).index_list().run(conn)
    files_list = r.table(FileCollections.Files).index_list().run(conn)
    file_server_list = r.table(FileCollections.FileServers).index_list().run(conn)
    tags_list = r.table(TagsCollection).index_list().run(conn)
    agents_list = r.table(AgentsCollection).index_list().run(conn)
    agent_operations_list = r.table(OperationCollections.Agent).index_list().run(conn)
    admin_operations_list = r.table(OperationCollections.Admin).index_list().run(conn)
    operations_per_agent_list = r.table(OperationCollections.OperationPerAgent).index_list().run(conn)
    operations_per_app_list = r.table(OperationCollections.OperationPerApp).index_list().run(conn)
    notif_list = r.table(NotificationCollections.Notifications).index_list().run(conn)
    notif_history_list = r.table(NotificationCollections.NotificationsHistory).index_list().run(conn)
    hw_per_agent_list = r.table(HardwarePerAgentCollection).index_list().run(conn)
    tag_per_agent_list = r.table(TagsPerAgentCollection).index_list().run(conn)
    notif_plugin_list = r.table(NotificationCollections.NotificationPlugins,).index_list().run(conn)
    agent_queue_list = r.table(QueueCollections.Agent).index_list().run(conn)
    groups_list = r.table(GroupCollections.Groups).index_list().run(conn)
    groups_per_user_list = r.table(GroupCollections.GroupsPerUser).index_list().run(conn)
    customer_per_user_list = r.table(CustomerCollections.CustomersPerUser).index_list().run(conn)

#################################### AgentsColleciton Indexes ###################################################
    if not AgentIndexes.CustomerName in agents_list:
        r.table(AgentsCollection).index_create(AgentIndexes.CustomerName).run(conn)

    if not AgentIndexes.OsCode in agents_list:
        r.table(AgentsCollection).index_create(AgentIndexes.OsCode).run(conn)

#################################### AppsCollection Indexes ###################################################
    if not AppsIndexes.RvSeverity in unique_app_list:
        r.table(AppCollections.UniqueApplications).index_create(AppsIndexes.RvSeverity).run(conn)

    if not AppsIndexes.Name in unique_app_list:
        r.table(AppCollections.UniqueApplications).index_create(AppsIndexes.Name).run(conn)

    if not AppsIndexes.NameAndVersion in unique_app_list:
        r.table(AppCollections.UniqueApplications).index_create(
            AppsIndexes.NameAndVersion, lambda x: [
                x[AppsKey.Name], x[AppsKey.Version]]).run(conn)

    if not AppsIndexes.Customers in unique_app_list:
        r.table(AppCollections.UniqueApplications).index_create(AppsIndexes.Customers, multi=True).run(conn)

    if not AppsIndexes.CustomerAndRvSeverity in unique_app_list:
        r.table(AppCollections.UniqueApplications).index_create(
            AppsIndexes.CustomerAndRvSeverity, lambda x: [
                x[AppsKey.Customers],
                x[AppsKey.RvSeverity]], multi=True).run(conn)

    if not AppsIndexes.AppIdAndRvSeverity in unique_app_list:
        r.table(AppCollections.UniqueApplications).index_create(
            AppsIndexes.AppIdAndRvSeverity, lambda x: [
                x[AppsKey.AppId],
                x[AppsKey.RvSeverity]]).run(conn)


#################################### FilesColleciton Indexes ###################################################
    if not FilesIndexes.FilesDownloadStatus in files_list:
        r.table(FileCollections.Files).index_create(FilesIndexes.FilesDownloadStatus).run(conn)

#################################### AppsPerAgentCollection Indexes ###################################################
    if not AppsPerAgentIndexes.Status in app_list:
        r.table(AppCollections.AppsPerAgent).index_create(AppsPerAgentIndexes.Status).run(conn)

    if not AppsPerAgentIndexes.AgentId in app_list:
        r.table(AppCollections.AppsPerAgent).index_create(AppsPerAgentIndexes.AgentId).run(conn)

    if not AppsPerAgentIndexes.AppId in app_list:
        r.table(AppCollections.AppsPerAgent).index_create(AppsPerAgentIndexes.AppId).run(conn)

    if not AppsPerAgentIndexes.CustomerName in app_list:
        r.table(AppCollections.AppsPerAgent).index_create(AppsPerAgentIndexes.CustomerName).run(conn)

    if not AppsPerAgentIndexes.AgentIdAndAppId in app_list:
        r.table(AppCollections.AppsPerAgent).index_create(
            AppsPerAgentIndexes.AgentIdAndAppId, lambda x: [
                x[AppsPerAgentKey.AgentId], x[AppsPerAgentKey.AppId]]).run(conn)

    if not AppsPerAgentIndexes.AppIdAndCustomer in app_list:
        r.table(AppCollections.AppsPerAgent).index_create(
            AppsPerAgentIndexes.AppIdAndCustomer, lambda x: [
                x[AppsPerAgentKey.AppId], x[AppsPerAgentKey.CustomerName]]).run(conn)

    if not AppsPerAgentIndexes.AppIdAndStatus in app_list:
        r.table(AppCollections.AppsPerAgent).index_create(
            AppsPerAgentIndexes.AppIdAndStatus, lambda x: [
                x[AppsPerAgentKey.AppId], x[AppsPerAgentKey.Status]]).run(conn)

    if not AppsPerAgentIndexes.StatusAndCustomer in app_list:
        r.table(AppCollections.AppsPerAgent).index_create(
            AppsPerAgentIndexes.StatusAndCustomer, lambda x: [
                x[AppsPerAgentKey.Status], x[AppsPerAgentKey.CustomerName]]).run(conn)

    if not AppsPerAgentIndexes.AppIdAndStatusAndCustomer in app_list:
        r.table(AppCollections.AppsPerAgent).index_create(
            AppsPerAgentIndexes.AppIdAndStatusAndCustomer, lambda x: [
                x[AppsPerAgentKey.AppId],
                x[AppsPerAgentKey.Status],
                x[AppsPerAgentKey.CustomerName]]).run(conn)

    if not AppsPerAgentIndexes.StatusAndAgentId in app_list:
        r.table(AppCollections.AppsPerAgent).index_create(
            AppsPerAgentIndexes.StatusAndAgentId, lambda x: [
                x[AppsPerAgentKey.Status], x[AppsPerAgentKey.AgentId]]).run(conn)


#################################### TagsCollection Indexes ###################################################
    if not TagsIndexes.CustomerName in tags_list:
        r.table(TagsCollection).index_create(TagsIndexes.CustomerName).run(conn)

    if not TagsIndexes.TagNameAndCustomer in tags_list:
        r.table(TagsCollection).index_create(
            TagsIndexes.TagNameAndCustomer, lambda x: [
                x[TagsKey.CustomerName], x[TagsKey.TagName]]).run(conn)

#################################### TagsPerAgentCollection Indexes ###################################################
    if not TagsPerAgentIndexes.TagId in tag_per_agent_list:
        r.table(TagsPerAgentCollection).index_create(TagsPerAgentIndexes.TagId).run(conn)

    if not TagsPerAgentIndexes.AgentId in tag_per_agent_list:
        r.table(TagsPerAgentCollection).index_create(TagsPerAgentIndexes.AgentId).run(conn)

    if not TagsPerAgentIndexes.AgentIdAndTagId in tag_per_agent_list:
        r.table(TagsPerAgentCollection).index_create(
            TagsPerAgentIndexes.AgentIdAndTagId, lambda x: [
                x[TagsPerAgentKey.AgentId],
                x[TagsPerAgentKey.TagId]]).run(conn)


#################################### CustomAppsCollection Indexes ###################################################
    if not CustomAppsIndexes.RvSeverity in custom_app_list:
        r.table(AppCollections.CustomApps).index_create(CustomAppsIndexes.RvSeverity).run(conn)

    if not CustomAppsIndexes.Name in custom_app_list:
        r.table(AppCollections.CustomApps).index_create(CustomAppsIndexes.Name).run(conn)

    if not CustomAppsIndexes.NameAndVersion in custom_app_list:
        r.table(AppCollections.CustomApps).index_create(
            CustomAppsIndexes.NameAndVersion, lambda x: [
                x[CustomAppsKey.Name], x[CustomAppsKey.Version]]).run(conn)

    if not CustomAppsIndexes.Customers in custom_app_list:
        r.table(AppCollections.CustomApps).index_create(CustomAppsIndexes.Customers, multi=True).run(conn)

    if not CustomAppsIndexes.CustomerAndRvSeverity in custom_app_list:
        r.table(AppCollections.CustomApps).index_create(
            CustomAppsIndexes.CustomerAndRvSeverity, lambda x: [
                x[CustomAppsKey.Customers], x[CustomAppsKey.RvSeverity]], multi=True).run(conn)

    if not CustomAppsIndexes.AppIdAndRvSeverity in custom_app_list:
        r.table(AppCollections.CustomApps).index_create(
            CustomAppsIndexes.AppIdAndRvSeverity, lambda x: [
                x[CustomAppsKey.AppId],
                x[CustomAppsKey.RvSeverity]]).run(conn)

#################################### CustomAppsPerAgentCollection Indexes ###################################################
    if not CustomAppsPerAgentIndexes.Status in custom_app_per_agent_list:
        r.table(AppCollections.CustomAppsPerAgent).index_create(CustomAppsPerAgentIndexes.Status).run(conn)

    if not CustomAppsPerAgentIndexes.AgentId in custom_app_per_agent_list:
        r.table(AppCollections.CustomAppsPerAgent).index_create(CustomAppsPerAgentIndexes.AgentId).run(conn)

    if not CustomAppsPerAgentIndexes.AppId in custom_app_per_agent_list:
        r.table(AppCollections.CustomAppsPerAgent).index_create(CustomAppsPerAgentIndexes.AppId).run(conn)

    if not CustomAppsPerAgentIndexes.CustomerName in custom_app_per_agent_list:
        r.table(AppCollections.CustomAppsPerAgent).index_create(CustomAppsPerAgentIndexes.CustomerName).run(conn)

    if not CustomAppsPerAgentIndexes.AgentIdAndAppId in custom_app_per_agent_list:
        r.table(AppCollections.CustomAppsPerAgent).index_create(
            CustomAppsPerAgentIndexes.AgentIdAndAppId, lambda x: [
                x[CustomAppsPerAgentKey.AgentId], x[CustomAppsPerAgentKey.AppId]]).run(conn)

    if not CustomAppsPerAgentIndexes.AppIdAndCustomer in custom_app_per_agent_list:
        r.table(AppCollections.CustomAppsPerAgent).index_create(
            CustomAppsPerAgentIndexes.AppIdAndCustomer, lambda x: [
                x[CustomAppsPerAgentKey.AppId], x[CustomAppsPerAgentKey.CustomerName]]).run(conn)

    if not CustomAppsPerAgentIndexes.AppIdAndStatus in custom_app_per_agent_list:
        r.table(AppCollections.CustomAppsPerAgent).index_create(
            CustomAppsPerAgentIndexes.AppIdAndStatus, lambda x: [
                x[CustomAppsPerAgentKey.AppId], x[CustomAppsPerAgentKey.Status]]).run(conn)

    if not CustomAppsPerAgentIndexes.StatusAndCustomer in custom_app_per_agent_list:
        r.table(AppCollections.CustomAppsPerAgent).index_create(
            CustomAppsPerAgentIndexes.StatusAndCustomer, lambda x: [
                x[CustomAppsPerAgentKey.Status], x[CustomAppsPerAgentKey.CustomerName]]).run(conn)

    if not CustomAppsPerAgentIndexes.AppIdAndStatusAndCustomer in custom_app_per_agent_list:
        r.table(AppCollections.CustomAppsPerAgent).index_create(
            CustomAppsPerAgentIndexes.AppIdAndStatusAndCustomer, lambda x: [
                x[CustomAppsPerAgentKey.AppId],
                x[CustomAppsPerAgentKey.Status],
                x[CustomAppsPerAgentKey.CustomerName]]).run(conn)

    if not CustomAppsPerAgentIndexes.StatusAndAgentId in custom_app_per_agent_list:
        r.table(AppCollections.CustomAppsPerAgent).index_create(
            CustomAppsPerAgentIndexes.StatusAndAgentId, lambda x: [
                x[CustomAppsPerAgentKey.Status], x[CustomAppsPerAgentKey.AgentId]]).run(conn)

#################################### SupportedAppsCollection Indexes ###################################################
    if not SupportedAppsIndexes.RvSeverity in supported_app_list:
        r.table(AppCollections.SupportedApps).index_create(SupportedAppsIndexes.RvSeverity).run(conn)

    if not SupportedAppsIndexes.Name in supported_app_list:
        r.table(AppCollections.SupportedApps).index_create(SupportedAppsIndexes.Name).run(conn)

    if not SupportedAppsIndexes.NameAndVersion in supported_app_list:
        r.table(AppCollections.SupportedApps).index_create(
            SupportedAppsIndexes.NameAndVersion, lambda x: [
                x[SupportedAppsKey.Name], x[SupportedAppsKey.Version]]).run(conn)

    if not SupportedAppsIndexes.Customers in supported_app_list:
        r.table(AppCollections.SupportedApps).index_create(SupportedAppsIndexes.Customers, multi=True).run(conn)

    if not SupportedAppsIndexes.CustomerAndRvSeverity in supported_app_list:
        r.table(AppCollections.SupportedApps).index_create(
            SupportedAppsIndexes.CustomerAndRvSeverity, lambda x: [
                x[SupportedAppsKey.Customers], x[SupportedAppsKey.RvSeverity]], multi=True).run(conn)

    if not SupportedAppsIndexes.AppIdAndRvSeverity in supported_app_list:
        r.table(AppCollections.SupportedApps).index_create(
            SupportedAppsIndexes.AppIdAndRvSeverity, lambda x: [
                x[SupportedAppsKey.AppId],
                x[SupportedAppsKey.RvSeverity]]).run(conn)

#################################### SupportedAppsPerAgentCollection Indexes ###################################################
    if not SupportedAppsPerAgentIndexes.Status in supported_app_per_agent_list:
        r.table(AppCollections.SupportedAppsPerAgent).index_create(SupportedAppsPerAgentIndexes.Status).run(conn)

    if not SupportedAppsPerAgentIndexes.AgentId in supported_app_per_agent_list:
        r.table(AppCollections.SupportedAppsPerAgent).index_create(SupportedAppsPerAgentIndexes.AgentId).run(conn)

    if not SupportedAppsPerAgentIndexes.AppId in supported_app_per_agent_list:
        r.table(AppCollections.SupportedAppsPerAgent).index_create(SupportedAppsPerAgentIndexes.AppId).run(conn)

    if not SupportedAppsPerAgentIndexes.CustomerName in supported_app_per_agent_list:
        r.table(AppCollections.SupportedAppsPerAgent).index_create(SupportedAppsPerAgentIndexes.CustomerName).run(conn)

    if not SupportedAppsPerAgentIndexes.AgentIdAndAppId in supported_app_per_agent_list:
        r.table(AppCollections.SupportedAppsPerAgent).index_create(
            SupportedAppsPerAgentIndexes.AgentIdAndAppId, lambda x: [
                x[SupportedAppsPerAgentKey.AgentId], x[SupportedAppsPerAgentKey.AppId]]).run(conn)

    if not SupportedAppsPerAgentIndexes.AppIdAndCustomer in supported_app_per_agent_list:
        r.table(AppCollections.SupportedAppsPerAgent).index_create(
            SupportedAppsPerAgentIndexes.AppIdAndCustomer, lambda x: [
                x[SupportedAppsPerAgentKey.AppId], x[SupportedAppsPerAgentKey.CustomerName]]).run(conn)

    if not SupportedAppsPerAgentIndexes.AppIdAndStatus in supported_app_per_agent_list:
        r.table(AppCollections.SupportedAppsPerAgent).index_create(
            SupportedAppsPerAgentIndexes.AppIdAndStatus, lambda x: [
                x[SupportedAppsPerAgentKey.AppId], x[SupportedAppsPerAgentKey.Status]]).run(conn)

    if not SupportedAppsPerAgentIndexes.StatusAndCustomer in supported_app_per_agent_list:
        r.table(AppCollections.SupportedAppsPerAgent).index_create(
            SupportedAppsPerAgentIndexes.StatusAndCustomer, lambda x: [
                x[SupportedAppsPerAgentKey.Status], x[SupportedAppsPerAgentKey.CustomerName]]).run(conn)

    if not SupportedAppsPerAgentIndexes.AppIdAndStatusAndCustomer in supported_app_per_agent_list:
        r.table(AppCollections.SupportedAppsPerAgent).index_create(
            SupportedAppsPerAgentIndexes.AppIdAndStatusAndCustomer, lambda x: [
                x[SupportedAppsPerAgentKey.AppId],
                x[SupportedAppsPerAgentKey.Status],
                x[SupportedAppsPerAgentKey.CustomerName]]).run(conn)

    if not SupportedAppsPerAgentIndexes.StatusAndAgentId in supported_app_per_agent_list:
        r.table(AppCollections.SupportedAppsPerAgent).index_create(
            SupportedAppsPerAgentIndexes.StatusAndAgentId, lambda x: [
                x[SupportedAppsPerAgentKey.Status], x[SupportedAppsPerAgentKey.AgentId]]).run(conn)

#################################### vFenseAppsCollection Indexes ###################################################
    if not vFenseAppsIndexes.RvSeverity in vfense_app_list:
        r.table(AppCollections.vFenseApps).index_create(AgentAppsIndexes.RvSeverity).run(conn)

    if not vFenseAppsIndexes.Name in vfense_app_list:
        r.table(AppCollections.vFenseApps).index_create(AgentAppsIndexes.Name).run(conn)

    if not vFenseAppsIndexes.NameAndVersion in vfense_app_list:
        r.table(AppCollections.vFenseApps).index_create(
            vFenseAppsIndexes.NameAndVersion, lambda x: [
                x[vFenseAppsKey.Name], x[vFenseAppsKey.Version]]).run(conn)

    if not vFenseAppsIndexes.Customers in vfense_app_list:
        r.table(AppCollections.vFenseApps).index_create(AgentAppsIndexes.Customers, multi=True).run(conn)

    if not vFenseAppsIndexes.CustomerAndRvSeverity in vfense_app_list:
        r.table(AppCollections.vFenseApps).index_create(
            vFenseAppsIndexes.CustomerAndRvSeverity, lambda x: [
                x[vFenseAppsKey.Customers], x[vFenseAppsKey.RvSeverity]], multi=True).run(conn)

    if not vFenseAppsIndexes.AppIdAndRvSeverity in vfense_app_list:
        r.table(AppCollections.vFenseApps).index_create(
            vFenseAppsIndexes.AppIdAndRvSeverity, lambda x: [
                x[vFenseAppsKey.AppId],
                x[vFenseAppsKey.RvSeverity]]).run(conn)

#################################### vFenseAppsPerAgentCollection Indexes ###################################################
    if not vFenseAppsPerAgentIndexes.Status in vfense_app_per_agent_list:
        r.table(AppCollections.vFenseAppsPerAgent).index_create(AgentAppsPerAgentIndexes.Status).run(conn)

    if not vFenseAppsPerAgentIndexes.AgentId in vfense_app_per_agent_list:
        r.table(AppCollections.vFenseAppsPerAgent).index_create(AgentAppsPerAgentIndexes.AgentId).run(conn)

    if not vFenseAppsPerAgentIndexes.AppId in vfense_app_per_agent_list:
        r.table(AppCollections.vFenseAppsPerAgent).index_create(AgentAppsPerAgentIndexes.AppId).run(conn)

    if not vFenseAppsPerAgentIndexes.CustomerName in vfense_app_per_agent_list:
        r.table(AppCollections.vFenseAppsPerAgent).index_create(AgentAppsPerAgentIndexes.CustomerName).run(conn)

    if not vFenseAppsPerAgentIndexes.AgentIdAndAppId in vfense_app_per_agent_list:
        r.table(AppCollections.vFenseAppsPerAgent).index_create(
            vFenseAppsPerAgentIndexes.AgentIdAndAppId, lambda x: [
                x[vFenseAppsPerAgentKey.AgentId], x[vFenseAppsPerAgentKey.AppId]]).run(conn)

    if not vFenseAppsPerAgentIndexes.AppIdAndCustomer in vfense_app_per_agent_list:
        r.table(AppCollections.vFenseAppsPerAgent).index_create(
            vFenseAppsPerAgentIndexes.AppIdAndCustomer, lambda x: [
                x[vFenseAppsPerAgentKey.AppId], x[vFenseAppsPerAgentKey.CustomerName]]).run(conn)

    if not vFenseAppsPerAgentIndexes.AppIdAndStatus in vfense_app_per_agent_list:
        r.table(AppCollections.vFenseAppsPerAgent).index_create(
            vFenseAppsPerAgentIndexes.AppIdAndStatus, lambda x: [
                x[vFenseAppsPerAgentKey.AppId], x[vFenseAppsPerAgentKey.Status]]).run(conn)

    if not vFenseAppsPerAgentIndexes.StatusAndCustomer in vfense_app_per_agent_list:
        r.table(AppCollections.vFenseAppsPerAgent).index_create(
            vFenseAppsPerAgentIndexes.StatusAndCustomer, lambda x: [
                x[vFenseAppsPerAgentKey.Status], x[vFenseAppsPerAgentKey.CustomerName]]).run(conn)

    if not vFenseAppsPerAgentIndexes.AppIdAndStatusAndCustomer in vfense_app_per_agent_list:
        r.table(AppCollections.vFenseAppsPerAgent).index_create(
            vFenseAppsPerAgentIndexes.AppIdAndStatusAndCustomer, lambda x: [
                x[vFenseAppsPerAgentKey.AppId],
                x[vFenseAppsPerAgentKey.Status],
                x[vFenseAppsPerAgentKey.CustomerName]]).run(conn)

    if not vFenseAppsPerAgentIndexes.StatusAndAgentId in vfense_app_per_agent_list:
        r.table(AppCollections.vFenseAppsPerAgent).index_create(
            vFenseAppsPerAgentIndexes.StatusAndAgentId, lambda x: [
                x[vFenseAppsPerAgentKey.Status], x[vFenseAppsPerAgentKey.AgentId]]).run(conn)


#################################### AgentOperationsCollection Indexes ###################################################
    if not AgentOperationIndexes.CustomerName in agent_operations_list:
        r.table(OperationCollections.Agent).index_create(AgentOperationKey.CustomerName).run(conn)

    if not AgentOperationIndexes.TagId in agent_operations_list:
        r.table(OperationCollections.Agent).index_create(AgentOperationKey.TagId).run(conn)

    if not AgentOperationIndexes.Operation in agent_operations_list:
        r.table(OperationCollections.Agent).index_create(AgentOperationKey.Operation).run(conn)

    if not AgentOperationIndexes.AgentIds in agent_operations_list:
        r.table(OperationCollections.Agent).index_create(AgentOperationIndexes.AgentIds, multi=True).run(conn)

    if not AgentOperationIndexes.OperationAndCustomer in agent_operations_list:
        r.table(OperationCollections.Agent).index_create(
            AgentOperationIndexes.OperationAndCustomer, lambda x: [
                x[AgentOperationKey.Operation],
                x[AgentOperationKey.CustomerName]]).run(conn)

    if not AgentOperationIndexes.PluginAndCustomer in agent_operations_list:
        r.table(OperationCollections.Agent).index_create(
            AgentOperationIndexes.PluginAndCustomer, lambda x: [
                x[AgentOperationKey.Plugin],
                x[AgentOperationKey.CustomerName]]).run(conn)

    if not AgentOperationIndexes.CreatedByAndCustomer in agent_operations_list:
        r.table(OperationCollections.Agent).index_create(
            AgentOperationIndexes.CreatedByAndCustomer, lambda x: [
                x[AgentOperationKey.CreatedBy],
                x[AgentOperationKey.CustomerName]]).run(conn)

#################################### OperationsPerAgentCollection Indexes ###################################################
    if not OperationPerAgentIndexes.OperationId in operations_per_agent_list:
        r.table(OperationCollections.OperationPerAgent).index_create(OperationPerAgentKey.OperationId).run(conn)

    if not OperationPerAgentIndexes.AgentIdAndCustomer in operations_per_agent_list:
        r.table(OperationCollections.OperationPerAgent).index_create(
            OperationPerAgentIndexes.AgentIdAndCustomer, lambda x: [
                x[OperationPerAgentKey.AgentId],
                x[OperationPerAgentKey.CustomerName]]).run(conn)

    if not OperationPerAgentIndexes.TagIdAndCustomer in operations_per_agent_list:
        r.table(OperationCollections.OperationPerAgent).index_create(
            OperationPerAgentIndexes.TagIdAndCustomer, lambda x: [
                x[OperationPerAgentKey.TagId],
                x[OperationPerAgentKey.CustomerName]]).run(conn)

    if not OperationPerAgentIndexes.StatusAndCustomer in operations_per_agent_list:
        r.table(OperationCollections.OperationPerAgent).index_create(
            OperationPerAgentIndexes.StatusAndCustomer, lambda x: [
                x[OperationPerAgentKey.Status],
                x[OperationPerAgentKey.CustomerName]]).run(conn)

    if not OperationPerAgentIndexes.OperationIdAndAgentId in operations_per_agent_list:
        r.table(OperationCollections.OperationPerAgent).index_create(
            OperationPerAgentIndexes.OperationIdAndAgentId, lambda x: [
                x[OperationPerAgentKey.OperationId],
                x[OperationPerAgentKey.AgentId]]).run(conn)

#################################### OperationsPerAppCollection Indexes ###################################################
    if not OperationPerAppIndexes.OperationId in operations_per_app_list:
        r.table(OperationCollections.OperationPerApp).index_create(OperationPerAppKey.OperationId).run(conn)

    if not OperationPerAppIndexes.OperationIdAndAgentId in operations_per_app_list:
        r.table(OperationCollections.OperationPerApp).index_create(
            OperationPerAppIndexes.OperationIdAndAgentId, lambda x: [
                x[OperationPerAppKey.OperationId],
                x[OperationPerAppKey.AgentId]]).run(conn)

    if not OperationPerAppIndexes.OperationIdAndAgentIdAndAppId in operations_per_app_list:
        r.table(OperationCollections.OperationPerApp).index_create(
            OperationPerAppIndexes.OperationIdAndAgentIdAndAppId, lambda x: [
                x[OperationPerAppKey.OperationId],
                x[OperationPerAppKey.AgentId],
                x[OperationPerAppKey.AppId]]).run(conn)

#################################### HardwarePerAgentCollection Indexes ###################################################
    if not HardwarePerAgentIndexes.Type in hw_per_agent_list:
        r.table(HardwarePerAgentCollection).index_create(HardwarePerAgentIndexes.Type).run(conn)

    if not HardwarePerAgentIndexes.AgentId in hw_per_agent_list:
        r.table(HardwarePerAgentCollection).index_create(HardwarePerAgentIndexes.AgentId).run(conn)

#################################### DownloadStatusCollection Indexes ###################################################
    if not 'app_id' in downloaded_list:
        r.table('downloaded_status').index_create('app_id').run(conn)

    if not 'by_filename_and_rvid' in downloaded_list:
        r.table('downloaded_status').index_create(
            'by_filename_and_rvid', lambda x: [
                x['file_name'], x['app_id']]).run(conn)

#################################### NotificationsCollection Indexes ###################################################
    if not NotificationIndexes.CustomerName in notif_list:
        r.table(NotificationCollections.Notifications).index_create(NotificationKeys.CustomerName).run(conn)

    if not NotificationIndexes.RuleNameAndCustomer in notif_list:
        r.table(NotificationCollections.Notifications).index_create(
            NotificationIndexes.RuleNameAndCustomer, lambda x: [
                x[NotificationKeys.RuleName],
                x[NotificationKeys.CustomerName]]).run(conn)

    if not NotificationIndexes.NotificationTypeAndCustomer in notif_list:
        r.table(NotificationCollections.Notifications).index_create(
            NotificationIndexes.NotificationTypeAndCustomer, lambda x: [
                x[NotificationKeys.NotificationType],
                x[NotificationKeys.CustomerName]]).run(conn)

    if not NotificationIndexes.AppThresholdAndCustomer in notif_list:
        r.table(NotificationCollections.Notifications).index_create(
            NotificationIndexes.AppThresholdAndCustomer, lambda x: [
                x[NotificationKeys.AppThreshold],
                x[NotificationKeys.CustomerName]]).run(conn)

    if not NotificationIndexes.RebootThresholdAndCustomer in notif_list:
        r.table(NotificationCollections.Notifications).index_create(
            NotificationIndexes.RebootThresholdAndCustomer, lambda x: [
                x[NotificationKeys.RebootThreshold],
                x[NotificationKeys.CustomerName]]).run(conn)

    if not NotificationIndexes.ShutdownThresholdAndCustomer in notif_list:
        r.table(NotificationCollections.Notifications).index_create(
            NotificationIndexes.ShutdownThresholdAndCustomer, lambda x: [
                x[NotificationKeys.ShutdownThreshold],
                x[NotificationKeys.CustomerName]]).run(conn)

    if not NotificationIndexes.CpuThresholdAndCustomer in notif_list:
        r.table(NotificationCollections.Notifications).index_create(
            NotificationIndexes.CpuThresholdAndCustomer, lambda x: [
                x[NotificationKeys.CpuThreshold],
                x[NotificationKeys.CustomerName]]).run(conn)

    if not NotificationIndexes.MemThresholdAndCustomer in notif_list:
        r.table(NotificationCollections.Notifications).index_create(
            NotificationIndexes.MemThresholdAndCustomer, lambda x: [
                x[NotificationKeys.MemThreshold],
                x[NotificationKeys.CustomerName]]).run(conn)

    if not NotificationIndexes.FileSystemThresholdAndFileSystemAndCustomer in notif_list:
        r.table(NotificationCollections.Notifications).index_create(
            NotificationIndexes.FileSystemThresholdAndFileSystemAndCustomer, lambda x: [
                x[NotificationKeys.FileSystemThreshold],
                x[NotificationKeys.FileSystem],
                x[NotificationKeys.CustomerName]]).run(conn)

#################################### NotificationsHistory Indexes ###################################################
    if not NotificationHistoryIndexes.NotificationId in notif_history_list:
        r.table(NotificationCollections.NotificationsHistory).index_create(NotificationHistoryKeys.NotificationId).run(conn)

#################################### NotificationsPlugin Indexes ###################################################
    if not NotificationPluginIndexes.CustomerName in notif_plugin_list:
        r.table(NotificationCollections.NotificationPlugins).index_create(NotificationPluginKeys.CustomerName).run(conn)

#################################### Cve Indexes ###################################################
    if not CveIndexes.CveCategories in cve_list:
        r.table(CVECollections.CVE).index_create(CveIndexes.CveCategories, multi=True).run(conn)

#################################### Windows Bulletin Indexes ###################################################
    if not WindowsSecurityBulletinIndexes.BulletinId in windows_bulletin_list:
        r.table(WindowsSecurityCollection.Bulletin).index_create(WindowsSecurityBulletinIndexes.BulletinId).run(conn)

    if not WindowsSecurityBulletinIndexes.ComponentKb in windows_bulletin_list:
        r.table(WindowsSecurityCollection.Bulletin).index_create(WindowsSecurityBulletinIndexes.ComponentKb).run(conn)

    if not WindowsSecurityBulletinIndexes.CveIds in windows_bulletin_list:
        r.table(WindowsSecurityCollection.Bulletin).index_create(WindowsSecurityBulletinIndexes.CveIds, multi=True).run(conn)
#################################### Ubuntu Bulletin Indexes ###################################################
    if not UbuntuSecurityBulletinIndexes.BulletinId in ubuntu_bulletin_list:
        r.table(UbuntuSecurityCollection.Bulletin).index_create(UbuntuSecurityBulletinIndexes.BulletinId).run(conn)

    if not UbuntuSecurityBulletinIndexes.NameAndVersion in ubuntu_bulletin_list:
        r.table(UbuntuSecurityCollection.Bulletin).index_create(
            UbuntuSecurityBulletinIndexes.NameAndVersion, lambda x: 
                x[UbuntuSecurityBulletinKey.Apps].map(lambda y:
                    [y['name'], y['version']]), multi=True).run(conn)

#################################### Agent Queue Indexes ###################################################
    if not AgentQueueIndexes.AgentId in agent_queue_list:
        r.table(QueueCollections.Agent).index_create(AgentQueueIndexes.AgentId).run(conn)

#################################### Group Indexes ###################################################
    if not GroupIndexes.CustomerName in groups_list:
        r.table(GroupCollections.Groups).index_create(GroupIndexes.CustomerName).run(conn)

    if not GroupIndexes.GroupName in groups_list:
        r.table(GroupCollections.Groups).index_create(GroupIndexes.GroupName).run(conn)

#################################### Groups Per User Indexes ###################################################
    if not GroupsPerUserIndexes.UserName in groups_per_user_list:
        r.table(GroupCollections.GroupsPerUser).index_create(GroupsPerUserIndexes.UserName).run(conn)

    if not GroupsPerUserIndexes.CustomerName in groups_per_user_list:
        r.table(GroupCollections.GroupsPerUser).index_create(GroupsPerUserIndexes.CustomerName).run(conn)

    if not GroupsPerUserIndexes.GroupName in groups_per_user_list:
        r.table(GroupCollections.GroupsPerUser).index_create(GroupsPerUserIndexes.GroupName).run(conn)

    if not GroupsPerUserIndexes.GroupId in groups_per_user_list:
        r.table(GroupCollections.GroupsPerUser).index_create(GroupsPerUserIndexes.GroupId).run(conn)

#################################### Customer Per User Indexes ###################################################
    if not CustomerPerUserIndexes.UserName in customer_per_user_list:
        r.table(CustomerCollections.CustomersPerUser).index_create(CustomerPerUserIndexes.UserName).run(conn)

    if not CustomerPerUserIndexes.CustomerName in customer_per_user_list:
        r.table(CustomerCollections.CustomersPerUser).index_create(CustomerPerUserIndexes.CustomerName).run(conn)

#################################### File Server Indexes ###################################################
    if not FileServerIndexes.CustomerName in file_server_list:
        r.table(FileCollections.FileServers).index_create(FileServerIndexes.CustomerName).run(conn)

#################################### Close Database Connection ###################################################
    conn.close()
