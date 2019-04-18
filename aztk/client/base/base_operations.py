from aztk import models
from aztk.internal import cluster_data

from .helpers import (create_user_on_cluster, create_user_on_node, delete_user_on_cluster, delete_user_on_node,
                      generate_user_on_cluster, generate_user_on_node, get_application_log, get_recent_job,
                      get_remote_login_settings, get_task_state, list_tasks, node_run, run, ssh_into_node, task_table)


class BaseOperations:
    """Base operations that all other operations have as an attribute

    Attributes:
        batch_client (:obj:`azure.batch.batch_service_client.BatchServiceClient`): Client used to interact with the
            Azure Batch service.
        blob_client (:obj:`azure.storage.blob.BlockBlobService`):  Client used to interact with the Azure Storage
            Blob service.
        secrets_configuration (:obj:`aztk.models.SecretsConfiguration`):
            Model that holds AZTK secrets used to authenticate with Azure and the clusters.
    """

    def __init__(self, context):
        self.batch_client = context["batch_client"]
        self.blob_client = context["blob_client"]
        self.table_service = context["table_service"]
        self.secrets_configuration = context["secrets_configuration"]

    def get_cluster_configuration(self, id: str) -> models.ClusterConfiguration:
        """Open an ssh tunnel to a node

        Args:
            id (:obj:`str`): the id of the cluster the node is in
            node_id (:obj:`str`): the id of the node to open the ssh tunnel to
            username (:obj:`str`): the username to authenticate the ssh session
            ssh_key (:obj:`str`, optional): ssh public key to create the user with, must use ssh_key
                or password. Defaults to None.
            password (:obj:`str`, optional): password for the user, must use ssh_key or password. Defaults to None.
            port_forward_list (:obj:`List[PortForwardingSpecification`, optional): list of PortForwardingSpecifications.
                The defined ports will be forwarded to the client.
            internal (:obj:`bool`, optional): if True, this will connect to the node using its internal IP.
                Only use this if running within the same VNET as the cluster. Defaults to False.

        Returns:
            :obj:`aztk.models.ClusterConfiguration`: Object representing the cluster's configuration
        """
        return self.get_cluster_data(id).read_cluster_config()

    def get_cluster_data(self, id: str) -> cluster_data.ClusterData:
        """Gets the ClusterData object to manage data related to the given cluster

        Args:
            id (:obj:`str`): the id of the cluster to get

        Returns:
            :obj:`aztk.models.ClusterData`: Object used to manage the data and storage functions for a cluster
        """
        return cluster_data.ClusterData(self.blob_client, id)

    def ssh_into_node(self, id, node_id, username, ssh_key=None, password=None, port_forward_list=None, internal=False):
        """Open an ssh tunnel to a node

        Args:
            id (:obj:`str`): the id of the cluster the node is in
            node_id (:obj:`str`): the id of the node to open the ssh tunnel to
            username (:obj:`str`): the username to authenticate the ssh session
            ssh_key (:obj:`str`, optional): ssh public key to create the user with, must use ssh_key or password.
                Defaults to None.
            password (:obj:`str`, optional): password for the user, must use ssh_key or password. Defaults to None.
            port_forward_list (:obj:`List[PortForwardingSpecification`, optional): list of PortForwardingSpecifications.
                The defined ports will be forwarded to the client.
            internal (:obj:`bool`, optional): if True, this will connect to the node using its internal IP.
                Only use this if running within the same VNET as the cluster. Defaults to False.

        Returns:
            :obj:`None`
        """
        ssh_into_node.ssh_into_node(self, id, node_id, username, ssh_key, password, port_forward_list, internal)

    def create_user_on_node(self, id, node_id, username, ssh_key=None, password=None):
        """Create a user on a node

        Args:
            id (:obj:`str`): id of the cluster to create the user on.
            node_id (:obj:`str`): id of the node in the cluster to create the user on.
            username (:obj:`str`): name of the user to create.
            ssh_key (:obj:`str`, optional): ssh public key to create the user with, must use ssh_key or password.
            password (:obj:`str`, optional): password for the user, must use ssh_key or password.

        Returns:
            :obj:`None`
        """
        return create_user_on_node.create_user_on_node(self, id, node_id, username, ssh_key, password)

    # TODO: remove nodes as param
    def create_user_on_cluster(self, id, nodes, username, ssh_pub_key=None, password=None):
        """Create a user on every node in the cluster

        Args:
            username (:obj:`str`): name of the user to create.
            id (:obj:`str`): id of the cluster to create the user on.
            nodes (:obj:`List[ComputeNode]`): list of nodes to create the user on
            ssh_key (:obj:`str`, optional): ssh public key to create the user with, must use ssh_key or password.
                Defaults to None.
            password (:obj:`str`, optional): password for the user, must use ssh_key or password. Defaults to None.

        Returns:
            :obj:`None`
        """
        return create_user_on_cluster.create_user_on_cluster(self, id, nodes, username, ssh_pub_key, password)

    def generate_user_on_node(self, id, node_id):
        """Create a user with an autogenerated username and ssh_key on the given node.

        Args:
            id (:obj:`str`): the id of the cluster to generate the user on.
            node_id (:obj:`str`): the id of the node in the cluster to generate the user on.

        Returns:
            :obj:`tuple`: A tuple of the form (username: :obj:`str`, ssh_key: :obj:`Cryptodome.PublicKey.RSA`)
        """
        return generate_user_on_node.generate_user_on_node(self, id, node_id)

    # TODO: remove nodes as param
    def generate_user_on_cluster(self, id, nodes):
        """Create a user with an autogenerated username and ssh_key on the cluster

        Args:
            id (:obj:`str`): the id of the cluster to generate the user on.
            node_id (:obj:`str`): the id of the node in the cluster to generate the user on.

        Returns:
            :obj:`tuple`: A tuple of the form (username: :obj:`str`, ssh_key: :obj:`Cryptodome.PublicKey.RSA`)
        """
        return generate_user_on_cluster.generate_user_on_cluster(self, id, nodes)

    def delete_user_on_node(self, id: str, node_id: str, username: str) -> str:
        """Delete a user on a node

        Args:
            id (:obj:`str`): the id of the cluster to delete the user on.
            node_id (:obj:`str`): the id of the node in the cluster to delete the user on.
            username (:obj:`str`): the name of the user to delete.

        Returns:
            :obj:`None`
        """
        return delete_user_on_node.delete_user(self, id, node_id, username)

    # TODO: remove nodes as param
    def delete_user_on_cluster(self, username, id, nodes):
        """Delete a user on every node in the cluster

        Args:
            id (:obj:`str`): the id of the cluster to delete the user on.
            node_id (:obj:`str`): the id of the node in the cluster to delete the user on.
            username (:obj:`str`): the name of the user to delete.

        Returns:
            :obj:`None`
        """
        return delete_user_on_cluster.delete_user_on_cluster(self, username, id, nodes)

    def node_run(self, id, node_id, command, internal, container_name=None, timeout=None, block=True):
        """Run a bash command on the given node

        Args:
            id (:obj:`str`): the id of the cluster to run the command on.
            node_id (:obj:`str`): the id of the node in the cluster to run the command on.
            command (:obj:`str`): the bash command to execute on the node.
            internal (:obj:`bool`): if True, this will connect to the node using its internal IP.
                Only use this if running within the same VNET as the cluster. Defaults to False.
            container_name=None (:obj:`str`, optional): the name of the container to run the command in.
                If None, the command will run on the host VM. Defaults to None.
            timeout=None (:obj:`str`, optional): The timeout in seconds for establishing a connection to the node.
                Defaults to None.
            block=True (:obj:`bool`, optional): If True, the command blocks until execution is complete.

        Returns:
            :obj:`aztk.models.NodeOutput`: object containing the output of the run command
        """
        return node_run.node_run(self, id, node_id, command, internal, container_name, timeout, block)

    def get_remote_login_settings(self, id: str, node_id: str):
        """Get the remote login information for a node in a cluster

        Args:
            id (:obj:`str`): the id of the cluster the node is in
            node_id (:obj:`str`): the id of the node in the cluster

        Returns:
            :obj:`aztk.models.RemoteLogin`: Object that contains the ip address and port combination to login to a node
        """
        return get_remote_login_settings.get_remote_login_settings(self, id, node_id)

    def run(self, id, command, internal, container_name=None, timeout=None):
        """Run a bash command on every node in the cluster

        Args:
            id (:obj:`str`): the id of the cluster to run the command on.
            command (:obj:`str`): the bash command to execute on the node.
            internal (:obj:`bool`): if true, this will connect to the node using its internal IP.
                Only use this if running within the same VNET as the cluster. Defaults to False.
            container_name=None (:obj:`str`, optional): the name of the container to run the command in.
                If None, the command will run on the host VM. Defaults to None.
            timeout=None (:obj:`str`, optional): The timeout in seconds for establishing a connection to the node.
                Defaults to None.

        Returns:
            :obj:`List[azkt.models.NodeOutput]`: list of NodeOutput objects containing the output of the run command
        """
        return run.cluster_run(self, id, command, internal, container_name, timeout)

    def get_application_log(self, id: str, application_name: str, tail=False, current_bytes: int = 0):
        """Get the log for a running or completed application

        Args:
            id (:obj:`str`): the id of the cluster to run the command on.
            application_name (:obj:`str`): str
            tail (:obj:`bool`, optional): If True, get the remaining bytes after current_bytes.
                Otherwise, the whole log will be retrieved. Only use this if streaming the log as it is being written.
                Defaults to False.
            current_bytes (:obj:`int`): Specifies the last seen byte, so only the bytes after current_bytes
                are retrieved. Only useful is streaming the log as it is being written. Only used if tail is True.

        Returns:
            :obj:`aztk.models.ApplicationLog`: a model representing the output of the application.
        """
        return get_application_log.get_application_log(self, id, application_name, tail, current_bytes)

    def create_task_table(self, id: str):
        """Create an Azure Table Storage to track tasks

        Args:
            id (:obj:`str`): the id of the cluster
        """
        return task_table.create_task_table(self.table_service, id)

    def list_task_table_entries(self, id):
        """list tasks in a storage table

        Args:
            id (:obj:`str`): the id of the cluster

        Returns:
            :obj:`[aztk.models.Task]`: a list of models representing all entries in the Task table
        """
        return task_table.list_task_table_entries(self.table_service, id)

    def get_task_from_table(self, id, task_id):
        """Create a storage table to track tasks

        Args:
            id (:obj:`str`): the id of the cluster

        Returns:
            :obj:`[aztk.models.Task]`: the task with id task_id from the cluster's storage table
        """
        return task_table.get_task_from_table(self.table_service, id, task_id)

    def insert_task_into_task_table(self, id, task):
        """Insert a task into the table

        Args:
            id (:obj:`str`): the id of the cluster

        Returns:
            :obj:`aztk.models.Task`: a model representing an entry in the Task table
        """
        return task_table.insert_task_into_task_table(self.table_service, id, task)

    def update_task_in_task_table(self, id, task):
        """Update a task in the table

        Args:
            id (:obj:`str`): the id of the cluster

        Returns:
            :obj:`aztk.models.Task`: a model representing an entry in the Task table
        """
        return task_table.update_task_in_task_table(self.table_service, id, task)

    def delete_task_table(self, id):
        """Delete the table that tracks tasks

        Args:
            id (:obj:`str`): the id of the cluster

        Returns:
            :obj:`bool`: if True, the deletion was successful
        """
        return task_table.delete_task_table(self.table_service, id)

    def list_tasks(self, id):
        """list tasks in a storage table

        Args:
            id (:obj:`str`): the id of the cluster

        Returns:
            :obj:`[aztk.models.Task]`: a list of models representing all entries in the Task table
        """
        return list_tasks.list_tasks(self, id)

    def get_recent_job(self, id):
        """Get the most recently run job in an Azure Batch job schedule

        Args:
            id (:obj:`str`): the id of the job schedule
        Returns:
            :obj:`[azure.batch.models.Job]`: the most recently run job on the job schedule
        """
        return get_recent_job.get_recent_job(self, id)

    def get_task_state(self, id: str, task_name: str):
        """Get the status of a submitted task

        Args:
            id (:obj:`str`): the name of the cluster the task was submitted to
            task_name (:obj:`str`): the name of the task to get

        Returns:
            :obj:`str`: the status state of the task
        """
        return get_task_state.get_task_state(self, id, task_name)

    def list_batch_tasks(self, id: str):
        """Get the status of a submitted task

        Args:
            id (:obj:`str`): the name of the cluster the task was submitted to

        Returns:
            :obj:`[aztk.models.Task]`: list of aztk tasks
        """
        return task_table.list_batch_tasks(self.batch_client, id)

    def get_batch_task(self, id: str, task_id: str):
        """Get the status of a submitted task

        Args:
            id (:obj:`str`): the name of the cluster the task was submitted to
            task_id (:obj:`str`): the name of the task to get

        Returns:
            :obj:`aztk.models.Task`: aztk Task representing the Batch Task
        """
        return task_table.get_batch_task(self.batch_client, id, task_id)
