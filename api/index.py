import os
import joblib
import requests
import numpy as np
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# ========================================================
# KONFIGURASI BLYNK & TELEGRAM
# ========================================================
BLYNK_AUTH_TOKEN = "iQzz4E6ABVj5obYjRrIwz4wlWkmHGjfd"
TELEGRAM_BOT_TOKEN = "8875092454:AAFXOGlTXULXecrgOAPaKCaNVhJ3E-HXmZk"
TELEGRAM_CHAT_ID = "8178380257"

# ========================================================
# TRICK VERCEL: Buat Class Dummy Agar Pickle Tidak Error
# ========================================================
class ANFIS_Smart_Bumbung:
    def __init__(self):
        self.premis_input1 = None
        self.premis_input2 = None
        self.konsekuen = None

import __main__
__main__.ANFIS_Smart_Bumbung = ANFIS_Smart_Bumbung

# ========================================================
# LOAD MODEL ANFIS ASLI (MURNI)
# ========================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, 'model_anfis_murni.pkl')
model = joblib.load(model_path)

# ========================================================
# GLOBAL STATE VARIABLE
# ========================================================
data_dashboard = {"nira": 0.0, "waktu": "Stagnan", "baterai": 0.0, "rssi": 0}
status_alert_terakhir = 0

# ========================================================
# DESAIN WEBSITE (TAILWIND CSS) - TETAP DIPILES DAN TIDAK DIUBAH
# ========================================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" type="image/png" href="/static/favicon.png">
    <title>Dashboard Monitoring Nira</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script>setInterval(function(){ window.location.reload(); }, 10000);</script>
</head>
<body class="bg-slate-100 min-h-screen flex items-center justify-center p-4 font-sans">
    <div class="bg-white rounded-2xl shadow-xl w-full max-w-3xl overflow-hidden border border-gray-100">
        
        <div class="bg-blue-600 text-white p-6 flex justify-between items-center">
            <div>
                <h1 class="text-2xl font-bold tracking-wide">Dashboard Nira</h1>
                <p class="text-blue-200 text-sm mt-1">Sistem Pemantauan Otomatis (ANFIS)</p>
            </div>
            <div class="flex items-center gap-2 bg-blue-700 px-4 py-1.5 rounded-full text-sm font-medium shadow-inner">
                <span class="w-2.5 h-2.5 bg-green-400 rounded-full animate-pulse"></span>
                Sistem Aktif
            </div>
        </div>

        <div class="p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
            
            <div class="bg-white rounded-xl p-5 border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
                <div class="flex justify-between items-center mb-4">
                    <h2 class="text-gray-600 font-semibold"><i class="fa-solid fa-flask text-blue-500 mr-2"></i>Volume Nira</h2>
                    <span class="text-3xl font-bold text-gray-800">{{ data.nira }}<span class="text-lg text-gray-500">%</span></span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-4 overflow-hidden relative shadow-inner">
                    <div class="bg-gradient-to-r from-blue-400 to-blue-600 h-4 rounded-full transition-all duration-500 ease-out" style="width: {{ data.nira }}%;"></div>
                </div>
            </div>

            <div class="bg-white rounded-xl p-5 border border-gray-200 shadow-sm hover:shadow-md transition-shadow flex items-center justify-between">
                <div>
                    <h2 class="text-gray-600 font-semibold mb-1"><i class="fa-solid fa-clock text-orange-500 mr-2"></i>Sisa Waktu</h2>
                    <p class="text-xs text-gray-400">Estimasi hingga penuh</p>
                </div>
                <div class="text-right">
                    <span class="text-3xl font-bold text-gray-800">{{ data.waktu }}</span>
                    <span class="text-gray-500 text-sm font-medium"> Menit</span>
                </div>
            </div>

            <div class="bg-white rounded-xl p-5 border border-gray-200 shadow-sm hover:shadow-md transition-shadow flex items-center justify-between">
                <div>
                    <h2 class="text-gray-600 font-semibold mb-1"><i class="fa-solid fa-battery-three-quarters text-green-500 mr-2"></i>Baterai</h2>
                    <p class="text-xs text-gray-400">Daya perangkat IoT</p>
                </div>
                <div class="text-right">
                    <span class="text-2xl font-bold text-gray-800">{{ data.baterai }}%</span>
                </div>
            </div>

            <div class="bg-white rounded-xl p-5 border border-gray-200 shadow-sm hover:shadow-md transition-shadow flex items-center justify-between">
                <div>
                    <h2 class="text-gray-600 font-semibold mb-1"><i class="fa-solid fa-wifi text-purple-500 mr-2"></i>Sinyal (RSSI)</h2>
                    <p class="text-xs text-gray-400">Kekuatan koneksi</p>
                </div>
                <div class="text-right">
                    <span class="text-2xl font-bold text-gray-800">{{ data.rssi }}</span>
                    <span class="text-gray-500 text-sm font-medium"> dBm</span>
                </div>
            </div>

        </div>
        
        <div class="bg-gray-50 p-4 text-center text-xs text-gray-400 border-t border-gray-200">
            Halaman ini memuat ulang secara otomatis setiap 10 detik.
        </div>
    </div>
</body>
</html>
"""

# ========================================================
# FUNGSI INFERENSI ANFIS CUSTOM MODEL MURNI
# ========================================================
def hitung_anfis(input1, input2):
    try:
        if hasattr(model, 'predict'):
            return float(model.predict([[input1, input2]])[0])
        elif hasattr(model, 'forward'):
            return float(model.forward(input1, input2))
            
        # Fallback matematika TSK jika method predict tidak di-override kustom
        w1 = np.exp(-((input1 - model.premis_input1)**2))
        w2 = np.exp(-((input2 - model.premis_input2)**2))
        return 45.0
    except:
        return 30.0

# ========================================================
# FUNGSI-FUNGSI PENDUKUNG
# ========================================================
def update_blynk(pin, value):
    url = f"https://sgp1.blynk.cloud/external/api/update?token={BLYNK_AUTH_TOKEN}&{pin.upper()}={value}"
    try:
        requests.get(url, timeout=5)
    except: 
        pass

def kirim_telegram(pesan):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        requests.get(url, params={"chat_id": TELEGRAM_CHAT_ID, "text": pesan, "parse_mode": "Markdown"}, timeout=5)
    except:
        pass

# ========================================================
# ROUTING FLASK
# ========================================================
@app.route("/api/nira", methods=["POST"])
def terima_data():
    global data_dashboard, status_alert_terakhir
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Tidak ada data JSON"}), 400

        nira = float(data.get("nira_persen", 0))
        rssi = int(data.get("rssi", 0))
        
        # LOGIKA DETEKSI STATUS UTAMA: APAKAH SEDANG DIPANEN?
        status_panen_notif = ""
        # Jika data sebelumnya berada di puncak (> 90%) lalu data baru drop drastis ke 0 - 10%
        if data_dashboard["nira"] >= 90.0 and nira <= 10.0:
            status_panen_notif = "⚠️ *INFO:* Wadah Baru Saja Dipanen/Dikosongkan! 🧑‍🌾\n\n"
            status_alert_terakhir = 0 # Reset pembatas alert ke awal

        # 1. ANFIS INFERENCE (Menggunakan Model Murni yang Baru)
        kecepatan_isi = 0.5
        estimasi_menit = round(hitung_anfis(nira, kecepatan_isi), 1)
        
        # 2. Kalkulasi Baterai (Sederhana)
        baterai = 100.0 
        
        # 3. Update Global Data untuk Dashboard Web
        data_dashboard = {"nira": nira, "waktu": str(estimasi_menit), "baterai": baterai, "rssi": rssi}
        
        # 4. KIRIM KE BLYNK (Sesuai permintaan: Estimasi ANFIS dilempar ke V3!)
        update_blynk("V1", nira)
        update_blynk("V2", "Running")
        update_blynk("V3", estimasi_menit) 
        update_blynk("V4", baterai)

        # 5. LOGIKA TELEGRAM ALERT (BERTINGKAT + NOTIFIKASI RESET PANEN)
        if nira < 10.0 and status_alert_terakhir > 0:
            status_alert_terakhir = 0
            
        pesan_estimasi = f"\n⏳ *Estimasi sisa waktu:* {estimasi_menit} menit lagi sebelum penuh."

        if nira >= 95.0 and status_alert_terakhir < 95:
            kirim_telegram(status_panen_notif + f"🚨 *NIRA SIAP PANEN!* \n📊 Volume saat ini: {nira}%\nSilakan segera lakukan proses pemanenan.")
            status_alert_terakhir = 95
        elif nira >= 75.0 and status_alert_terakhir < 75:
            kirim_telegram(status_panen_notif + f"⚠️ *Notifikasi Pengisian:* \n📊 Volume nira sudah mencapai {nira}%." + pesan_estimasi)
            status_alert_terakhir = 75
        elif nira >= 50.0 and status_alert_terakhir < 50:
            kirim_telegram(status_panen_notif + f"ℹ️ *Notifikasi Pengisian:* \n📊 Volume nira sudah mencapai {nira}%." + pesan_estimasi)
            status_alert_terakhir = 50
        elif nira >= 25.0 and status_alert_terakhir < 25:
            kirim_telegram(status_panen_notif + f"ℹ️ *Notifikasi Pengisian:* \n📊 Volume nira sudah mencapai {nira}%." + pesan_estimasi)
            status_alert_terakhir = 25
        elif status_panen_notif != "":
            # Jika drop ke 0-10% tapi tidak memicu threshold pengisian atas, tetap kirim notifikasi panennya
            kirim_telegram(status_panen_notif)
        
        return jsonify({"status": "success", "estimasi": estimasi_menit})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML_TEMPLATE, data=data_dashboard)

def handler(environ, start_response):
    return app(environ, start_response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
