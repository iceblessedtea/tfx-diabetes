"""
Module file used by TFX Trainer (defines run_fn).

This uses the transformed examples and transform_graph to build input_fn
and trains a simple Keras binary classifier.
"""

import tensorflow as tf
import tensorflow_transform as tft
from tfx.components.trainer.fn_args_utils import FnArgs


# Keys
LABEL_KEY = 'Outcome'

FEATURE_KEYS = [
    'Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness',
    'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age'
]

# Transformed features (Age_bucket ditambahkan)
TRANSFORMED_FEATURE_KEYS = FEATURE_KEYS + ['Age_bucket']

# Training parameters
BATCH_SIZE = 32
EPOCHS = 20


def _input_fn(file_pattern, data_accessor, tf_transform_output,
              batch_size=32, is_training=True):
    """
    Create input function for training/eval using TFX DataAccessor.

    Returns a tf.data.Dataset object.
    """

    # Load transformed feature specification
    transformed_feature_spec = tf_transform_output.transformed_feature_spec()

    # Create dataset using TFX helper
    dataset = data_accessor.tf_dataset_factory(
        file_pattern,
        tf_transform_output.transformed_metadata.schema,
        batch_size=batch_size,
        label_key=LABEL_KEY,
    )

    return dataset


def _build_keras_model(feature_spec):
    """Build simple Keras model based on transformed features."""

    # Create input layer for each transformed feature
    inputs = {
        key: tf.keras.Input(shape=(1,), name=key)
        for key in TRANSFORMED_FEATURE_KEYS
    }

    # Concatenate all input tensors
    concatenated = tf.keras.layers.Concatenate()(list(inputs.values()))

    # Dense layers
    x = tf.keras.layers.Dense(64, activation='relu')(concatenated)
    x = tf.keras.layers.Dropout(0.2)(x)
    x = tf.keras.layers.Dense(32, activation='relu')(x)
    outputs = tf.keras.layers.Dense(1, activation='sigmoid')(x)

    model = tf.keras.Model(inputs=inputs, outputs=outputs)

    # Compile model
    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=[
            tf.keras.metrics.AUC(name='auc'),
            tf.keras.metrics.Precision(name='precision'),
            tf.keras.metrics.Recall(name='recall')
        ]
    )

    return model


def run_fn(fn_args: FnArgs):
    """
    TFX Trainer run_fn entrypoint.

    fn_args provides:
    - train_files
    - eval_files
    - data_accessor
    - transform_output
    - serving_model_dir
    """
    # Load transform graph / transformed metadata
    tf_transform_output = tft.TFTransformOutput(fn_args.transform_output)

    # Build training & eval datasets
    train_dataset = _input_fn(
        fn_args.train_files,
        fn_args.data_accessor,
        tf_transform_output,
        batch_size=BATCH_SIZE,
        is_training=True
    )

    eval_dataset = _input_fn(
        fn_args.eval_files,
        fn_args.data_accessor,
        tf_transform_output,
        batch_size=BATCH_SIZE,
        is_training=False
    )

    # Build model
    feature_spec = tf_transform_output.transformed_feature_spec()
    model = _build_keras_model(feature_spec)

    # Train model
    model.fit(
        train_dataset,
        validation_data=eval_dataset,
        epochs=EPOCHS
    )

    # Save the model to the serving directory expected by TFX
    model.save(fn_args.serving_model_dir, save_format='tf')
