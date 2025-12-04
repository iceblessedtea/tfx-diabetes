# 🧬 TFX Diabetes ML Pipeline — Airflow + Astro Workflow

Repositori ini berisi percobaan saya dalam membangun *end-to-end machine learning pipeline* menggunakan **TensorFlow Extended (TFX)** dengan orkestrasi **Apache Airflow** dan **Astro Runtime (Docker)**. Pipeline ini menggunakan dataset `diabetes.csv` dan mencakup proses:

* ETL (Extract–Transform–Load)
* Normalisasi dan preprocessing menggunakan TF Transform
* Training model Keras
* Evaluasi dengan slicing metrics
* Deployment menggunakan Pusher

---

## 📌 1. Struktur Proyek

```
airflow-tfx-diabetes/
│
├── data/
│   └── diabetes.csv
│
├── pipeline/
│   ├── preprocess.py
│   ├── trainer_module.py
│   ├── components.py
│   └── pipeline.py
│
├── dags/
│   └── tfx_airflow_dag.py
│
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## 📌 2. Tujuan Proyek

1. Menjalankan **pipeline TFX lengkap** menggunakan Airflow.
2. Menggunakan Astro CLI (`astro dev start`) sebagai orchestrator.
3. Membuat model Keras yang dilatih dari data yang sudah ditransformasi TFX.
4. Melakukan evaluasi berbasis slice (`Age_bucket`).
5. Men-*deploy* model ke folder `serving_model/`.

---

# ✅ 3. Apa Saja yang Berhasil

### ✔ 1. Penulisan Pipeline TFX Berhasil

Pipeline berhasil dibuat dengan komponen-komponen:

* `CsvExampleGen`
* `StatisticsGen`
* `SchemaGen`
* `ExampleValidator`
* `Transform`
* `Trainer`
* `Evaluator`
* `Pusher`

---

### ✔ 2. Preprocessing Function TFX Berhasil Dibuat

File `preprocess.py` berhasil memuat fungsi:

* Normalisasi fitur numerik (`tft.scale_to_z_score`)
* Bucketization age (`tft.bucketize`)
* Output signature sesuai TFX

---

### ✔ 3. Trainer Module Berhasil Dibuat

Model Keras dengan input multi-feature berhasil ditulis:

* Dense → Dropout → Dense → Sigmoid
* Metrik: AUC, Precision, Recall
* Menggunakan transform_graph dari Transform

---

### ✔ 4. Pipeline Berhasil Diuji di LocalDagRunner (TFX murni)

Pipeline **berhasil berjalan di WSL Ubuntu** menggunakan LocalDagRunner:

```
python pipeline/pipeline.py
```

Output:

* Transform OK
* Trainer OK
* Model berhasil dipush ke folder serving

---

### ✔ 5. WSL Ubuntu Berhasil Dipakai Untuk Instalasi TFX

WSL mendukung Python 3.9 dan dapat menginstal:

```
pip install tfx==1.16.0 tensorflow==2.11.0
```

Pipeline berjalan lancar.

---

# ❌ 4. Apa Saja yang Tidak Berhasil

### ❌ 1. Instalasi TFX di Docker Astro Runtime

Airflow Astro Runtime menggunakan Python 3.10.

Masalah besar:

* TFX hanya kompatibel sampai Python 3.9
* Astro Runtime **tidak menyediakan** image Python 3.9
* Dependency conflict: TensorFlow + Apache Beam + TFX

Hasil error:

```
ERROR: No matching distribution found for tfx==1.24.0
```

---

### ❌ 2. Tidak Bisa Build Docker Image dengan TFX

Karena pip index Astronomer tidak menyediakan wheel TFX.

---

### ❌ 3. Tidak Bisa Menggabungkan TFX + Astro + Docker

* TFX mengunci versi Python
* Astro mengunci Python 3.10
* Beam + TensorFlow konflik

➡ **Integrasi TFX + Airflow Astro tidak memungkinkan secara versi.**

---

# 📌 5. Solusi Alternatif yang Berhasil

### ✔ Menjalankan pipeline TFX murni di WSL (Ubuntu)

Dengan Python 3.9:

```
sudo apt install python3.9 python3.9-venv
python3.9 -m venv venv
source venv/bin/activate
pip install tfx==1.16.0 tensorflow==2.11.0
```

Lalu jalankan pipeline:

```
python pipeline/pipeline.py
```

---

# 📌 6. Cara Menjalankan Pipeline TFX di WSL

### 1. Buat virtualenv Python 3.9

```
sudo apt install python3.9 python3.9-venv
python3.9 -m venv venv
source venv/bin/activate
```

### 2. Install dependency

```
pip install tfx==1.16.0 tensorflow==2.11.0
```

### 3. Jalankan pipeline

```
python pipeline/pipeline.py
```

Model akan muncul di:

```
/output/serving_model/
```

---

# 📌 7. Kesimpulan

| Komponen             | Status              |
| -------------------- | ------------------- |
| TFX Pipeline         | ✔ Berjalan          |
| Transform            | ✔ Berhasil          |
| Trainer              | ✔ Berhasil          |
| Evaluator            | ✔ Berhasil          |
| Pusher               | ✔ Output savedmodel |
| Integrasi Airflow    | ❌ Tidak kompatibel  |
| Docker Build (Astro) | ❌ Gagal             |

**Kesimpulan:**
TFX **tidak kompatibel dengan Airflow Astro (Python 3.10)** sehingga tidak dapat dijalankan melalui Docker Astro Runtime. Solusi terbaik adalah menjalankan TFX **murni di WSL**.

---

# 📌 8. License

MIT License.
