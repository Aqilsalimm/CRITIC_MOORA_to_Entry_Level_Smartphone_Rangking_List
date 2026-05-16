import os
# pyrefly: ignore [missing-import]
from flask import Flask, request, jsonify
import pandas as pd
from .dss_engine import hitung_rekomendasi

app = Flask(__name__)

# Membaca dataset CSV ke memory saat server Flask dijalankan pertama kali
csv_path = os.path.join(os.path.dirname(__file__), 'dataset_smartphone.csv')
try:
    df_master = pd.read_csv(csv_path)
    if 'C1' in df_master.columns:
        df_master['C1'] = pd.to_numeric(df_master['C1'], errors='coerce')
except FileNotFoundError:
    df_master = pd.DataFrame() # Fallback jika file belum ada

@app.route('/api/rekomendasi', methods=['POST'])
def rekomendasi_api():
    if df_master.empty:
        return jsonify({"error": "Dataset CSV tidak ditemukan di server"}), 500

    try:
        req_data = request.json
        max_price = req_data.get('max_price', 4000000)
        brands = req_data.get('brands', [])
        fokus_kriteria = req_data.get('fokus_kriteria', []) # Array berisi max 3 ID (contoh: ['C1', 'C4'])

        # 1. Filter Data Berdasarkan Parameter Dasar (Harga & Brand)
        # Asumsi kolom harga di CSV bernama 'Harga_USD' atau disesuaikan dengan C1
        df_filtered = df_master[df_master['C1'] <= float(max_price)].copy()
        
        if brands: # Jika user memilih brand tertentu
            df_filtered = df_filtered[df_filtered['Brand'].isin(brands)]

        if df_filtered.empty:
            return jsonify([]), 200 # Tidak ada HP yang sesuai

        # 2. Proses DSS
        # Fokus Kriteria yang dipilih user akan dikirim ke dss_engine 
        # untuk diberi bobot lebih besar secara matematis saat dihitung dengan metode ROC/CRITIC.
        hasil_rekomendasi = hitung_rekomendasi(df_filtered, fokus_kriteria)
        
        return jsonify(hasil_rekomendasi), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)