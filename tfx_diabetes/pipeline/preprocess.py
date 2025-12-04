import tensorflow_transform as tft

# Label kolom
LABEL_KEY = 'Outcome'

# Fitur numerik
FEATURE_KEYS = [
    'Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness',
    'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age'
]

# Jumlah bucket Age untuk slicing
AGE_BUCKETS = 3


def preprocessing_fn(inputs):
    """
    TFX preprocessing_fn.

    Proses:
    - Normalisasi fitur numerik menggunakan z-score (tft.scale_to_z_score)
    - Membuat kolom Age_bucket untuk slicing / evaluasi model
    - Menyalin label apa adanya
    """
    outputs = {}

    # Normalisasi semua fitur numerik
    for key in FEATURE_KEYS:
        value = inputs[key]
        outputs[key] = tft.scale_to_z_score(value)

    # Bucketize Age menjadi 3 kategori
    age = inputs['Age']
    age_buckets = tft.bucketize(age, num_buckets=AGE_BUCKETS)
    outputs['Age_bucket'] = age_buckets

    # Copy label
    outputs[LABEL_KEY] = inputs[LABEL_KEY]

    return outputs
