from azure.batch.models import BatchErrorException

from aztk import error
from aztk.utils import helpers


def cluster_copy(
        core_cluster_operations,
        cluster_id: str,
        source_path: str,
        destination_path: str,
        host: bool = False,
        internal: bool = False,
        timeout: int = None,
):
    try:
        container_name = None if host else "spark"
        return core_cluster_operations.copy(
            cluster_id,
            source_path,
            destination_path=destination_path,
            container_name=container_name,
            get=False,
            internal=internal,
            timeout=timeout,
        )
    except BatchErrorException as e:
        raise error.AztkError(helpers.format_batch_exception(e))
