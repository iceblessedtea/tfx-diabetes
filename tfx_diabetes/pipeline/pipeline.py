import os
import tfx

from tfx.orchestration import metadata
from tfx.orchestration.local import local_dag_runner
from tfx.proto import metadata_store_pb2

from .components import create_components


# Project base path
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
PIPELINE_ROOT = os.path.join(PROJECT_ROOT, 'output')
METADATA_PATH = os.path.join(PROJECT_ROOT, 'output', 'metadata.db')


def create_pipeline(data_root):
    """Create TFX pipeline for diabetes dataset."""

    components = create_components(data_root)

    pipeline = tfx.dsl.Pipeline(
        pipeline_name='tfx_diabetes_pipeline',
        pipeline_root=PIPELINE_ROOT,
        components=components,
        enable_cache=True,
        metadata_connection_config=metadata.sqlite_metadata_connection_config(
            METADATA_PATH
        )
    )

    return pipeline


if __name__ == '__main__':
    data_root = os.path.join(PROJECT_ROOT, 'data')
    pipeline = create_pipeline(data_root)

    # Run using LocalDagRunner
    local_dag_runner.LocalDagRunner().run(pipeline)
