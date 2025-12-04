import os

from tfx.components import (
    CsvExampleGen, StatisticsGen, SchemaGen, ExampleValidator,
    Transform, Trainer, Evaluator, Pusher
)
from tfx.proto import trainer_pb2, pusher_pb2, evaluator_pb2
from tfx.utils.dsl_utils import external_input


# Base project paths
PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_ROOT = os.path.join(PROJECT_DIR, 'data')
MODULE_FILE = os.path.join(PROJECT_DIR, 'pipeline', 'trainer_module.py')


def create_components(root):
    """Create all TFX pipeline components."""

    # 1. ExampleGen (load CSV)
    example_gen = CsvExampleGen(input=external_input(root))

    # 2. StatisticsGen → SchemaGen → ExampleValidator
    stats_gen = StatisticsGen(examples=example_gen.outputs['examples'])

    schema_gen = SchemaGen(
        statistics=stats_gen.outputs['statistics'],
        infer_feature_shape=False
    )

    example_validator = ExampleValidator(
        statistics=stats_gen.outputs['statistics'],
        schema=schema_gen.outputs['schema']
    )

    # 3. Transform component (using preprocess.py)
    transform = Transform(
        examples=example_gen.outputs['examples'],
        schema=schema_gen.outputs['schema'],
        module_file=os.path.join(os.path.dirname(__file__), 'preprocess.py')
    )

    # 4. Trainer
    trainer = Trainer(
        module_file=MODULE_FILE,
        examples=transform.outputs['transformed_examples'],
        transform_graph=transform.outputs['transform_graph'],
        schema=schema_gen.outputs['schema'],
        train_args=trainer_pb2.TrainArgs(num_steps=1000),
        eval_args=trainer_pb2.EvalArgs(num_steps=200)
    )

    # 5. Evaluator + Slicing (Age_bucket)
    slicing_spec = evaluator_pb2.SlicingSpec()
    slicing_spec.specs.add()  # Global slice

    bucket_slice = slicing_spec.specs.add()
    bucket_slice.feature_keys.extend(['Age_bucket'])

    evaluator = Evaluator(
        examples=example_gen.outputs['examples'],
        model_exports=trainer.outputs['model'],
        baseline_model=trainer.outputs['model'],
        slicing_specs=slicing_spec
    )

    # 6. Pusher (push only if model is blessed)
    pusher = Pusher(
        model=trainer.outputs['model'],
        model_blessing=evaluator.outputs['blessing'],
        push_destination=pusher_pb2.PushDestination(
            filesystem=pusher_pb2.PushDestination.Filesystem(
                base_directory=os.path.join(PROJECT_DIR, 'serving_model')
            )
        )
    )

    # Return all components
    return [
        example_gen,
        stats_gen,
        schema_gen,
        example_validator,
        transform,
        trainer,
        evaluator,
        pusher,
    ]
