# 🌴 Smart Bumbung - Monitoring Nira Berbasis IoT & ANFIS

Sistem monitoring nira berbasis **ESP32 + LoRa + Flask + ANFIS** untuk memantau volume nira secara real-time, menghitung estimasi waktu penuh menggunakan model ANFIS, serta mengirim notifikasi ke Telegram dan Blynk.

---

## 🚀 Fitur Utama

* Monitoring volume nira real-time
* Prediksi estimasi waktu penuh menggunakan **ANFIS**
* Dashboard web berbasis Flask + Tailwind CSS
* Monitoring RSSI (kekuatan sinyal)
* Integrasi dengan **Blynk IoT**
* Notifikasi Telegram otomatis
* Deployment cloud menggunakan **Vercel**

---

## 🛠 Tech Stack

### Hardware

* ESP32
* Modul LoRa
* Sensor ultrasonik / sensor level nira
* Baterai / power supply

### Software

* Python 3
* Flask
* NumPy
* Joblib
* Tailwind CSS
* Vercel

### IoT Platform

* Blynk Cloud
* Telegram Bot API

---

## 📂 Struktur Project

```bash
monitoring-nira-cloud/
│
├── api/
│   ├── index.py
│   ├── model_anfis.pkl
│   └── model_anfis_murni.pkl
│
├── static/
│   └── favicon.png
│
├── requirements.txt
├── vercel.json
└── README.md
```

---

## ⚙️ Cara Install

Clone repository:

```bash
git clone https://github.com/USERNAME/monitoring-nira-cloud.git
cd monitoring-nira-cloud
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run local:

```bash
python api/index.py
```

Server berjalan di:

```bash
http://localhost:5000
```

---

## 🌐 API Endpoint

### Home Dashboard

```http
GET /
```

Menampilkan dashboard monitoring nira.

---

### Kirim Data Sensor

```http
POST /api/nira
```

Body JSON:

```json
{
  "nira_persen": 75,
  "rssi": -87
}
```

Response:

```json
{
  "status": "success",
  "estimasi": 42.5
}
```

---

## 🧠 Model ANFIS

Input:

* Volume Nira (%)
* Kecepatan Pengisian (%/menit)

Output:

* Estimasi waktu hingga penuh (menit)

ANFIS digunakan untuk meningkatkan akurasi prediksi dibanding metode linear biasa.

---

## 📱 Integrasi Notifikasi

### Telegram Alert

Notifikasi dikirim saat volume mencapai:

* 25%
* 50%
* 75%
* 95% (Siap panen)

### Blynk Monitoring

Virtual Pin:

* V1 → Volume Nira
* V2 → Status Sistem
* V3 → Estimasi Waktu ANFIS
* V4 → Status Baterai

---

## 📸 Dashboard Preview

Tambahkan screenshot dashboard di sini.

---

## ☁️ Deployment

Project dideploy menggunakan:

* Vercel (Backend + Dashboard)
* ESP32 sebagai data sender

---

## 👨‍💻 Author

Developed by **Danu Wahyurinata**

---

## 📜 License

MIT License
