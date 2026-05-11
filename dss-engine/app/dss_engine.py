import pandas as pd
import numpy as np

def hitung_rekomendasi(df, fokus_kriteria):
    """
    Fungsi untuk menghitung rekomendasi menggunakan metode CRITIC dan MOORA.
    Menerima DataFrame yang sudah difilter dan daftar kriteria fokus.
    Mendukung C1-C9 dengan encoding untuk kriteria string (C7, C8, C9).
    """
    kriteria_cols = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9']
    
    # Tambahkan kolom Nama_HP jika belum ada (karena di dataset adanya Type)
    if 'Nama_HP' not in df.columns:
        df['Nama_HP'] = df['Brand'] + ' ' + df['Type']
        
    # 1. Encoding untuk kriteria non-numerik (C7, C8, C9) agar bisa dihitung
    mapping_c7 = {'eMMC': 1, 'UFS': 2}
    mapping_c8 = {'TFT': 1, 'IPS': 1, 'Amoled': 2, 'AMOLED': 2}
    mapping_c9 = {'HD+': 1, 'FHD': 2, 'FHD+': 3, '1.5K': 4}
    
    # Salin data agar tidak merusak dataframe asli untuk tampilan
    df_numeric = df.copy()
    
    if 'C7' in df_numeric.columns:
        df_numeric['C7'] = df_numeric['C7'].map(mapping_c7).fillna(1)
    if 'C8' in df_numeric.columns:
        df_numeric['C8'] = df_numeric['C8'].map(mapping_c8).fillna(1)
    if 'C9' in df_numeric.columns:
        df_numeric['C9'] = df_numeric['C9'].map(mapping_c9).fillna(1)
        
    # Pastikan semua kolom kriteria ada dan bernilai numerik
    for col in kriteria_cols:
        if col not in df_numeric.columns:
            df_numeric[col] = 0.0
        df_numeric[col] = pd.to_numeric(df_numeric[col], errors='coerce').fillna(0)
        
    X = df_numeric[kriteria_cols].values.astype(float)
    
    if X.shape[0] == 0:
        return []
        
    # --- 1. METODE CRITIC (Pembobotan Otomatis) ---
    # Normalisasi Min-Max
    min_val = X.min(axis=0)
    max_val = X.max(axis=0)
    range_val = max_val - min_val
    range_val[range_val == 0] = 1 # Hindari pembagian dengan nol
    X_norm = (X - min_val) / range_val
    
    # Standar Deviasi
    std_dev = np.std(X_norm, axis=0, ddof=1) if X.shape[0] > 1 else np.zeros(X.shape[1])
    
    # Matrix Korelasi
    if X.shape[0] > 1:
        correlation_matrix = np.corrcoef(X_norm, rowvar=False)
        correlation_matrix = np.nan_to_num(correlation_matrix)
    else:
        correlation_matrix = np.eye(X.shape[1])
        
    # Menghitung C_j
    num_criteria = X.shape[1]
    C_j = np.zeros(num_criteria)
    for j in range(num_criteria):
        sum_correlation = 0
        for k in range(num_criteria):
            sum_correlation += (1 - correlation_matrix[j, k])
        C_j[j] = std_dev[j] * sum_correlation
        
    # Bobot Akhir Wj (CRITIC)
    sum_Cj = np.sum(C_j)
    W_j = C_j / sum_Cj if sum_Cj > 0 else np.ones(num_criteria) / num_criteria
    
    # --- Modifikasi Bobot Berdasarkan Fokus Kriteria Pengguna ---
    if fokus_kriteria:
        for c_id in fokus_kriteria:
            if c_id in kriteria_cols:
                idx = kriteria_cols.index(c_id)
                W_j[idx] *= 2.0 # Berikan bobot 2x lebih besar untuk kriteria fokus
        # Re-normalisasi agar total bobot tetap 1
        W_j = W_j / np.sum(W_j)
    
    # --- 2. METODE MOORA (Perankingan) ---
    # Pembagi untuk normalisasi vektor
    pembagi = np.sqrt(np.sum(X**2, axis=0))
    pembagi[pembagi == 0] = 1
    X_norm_moora = X / pembagi
    
    # Matriks Normalisasi Terbobot
    X_weighted = X_norm_moora * W_j
    
    # C1 adalah Cost (Harga), C2-C9 adalah Benefit
    nilai_cost = X_weighted[:, 0]
    nilai_benefit = np.sum(X_weighted[:, 1:], axis=1)
    
    Yi = nilai_benefit - nilai_cost
    df_numeric['Nilai_Optimasi_Yi'] = Yi
    
    # Urutkan dari nilai Yi terbesar
    df_rank = df_numeric.sort_values(by='Nilai_Optimasi_Yi', ascending=False).reset_index(drop=True)
    
    # 1. Formatting Data Rekomendasi
    df_rank['Peringkat'] = df_rank.index + 1
    df_rank['Nama_HP'] = df_rank['Brand'] + ' ' + df_rank['Type']
    cols_display = ['Peringkat', 'Nama_HP', 'Brand', 'Nilai_Optimasi_Yi', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9']
    if 'Brand' not in df_rank.columns:
        df_rank['Brand'] = 'Unknown'
    hasil_rekomendasi = df_rank[cols_display].head(10).to_dict(orient='records')

    # 2. Pembuatan Data Analisis untuk Grafik
    # Ubah bobot W_j (desimal) menjadi persentase (%)
    bobot_persen = np.round(W_j * 100, 2)
    kriteria_cols = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9']
    
    # Mapping bobot ke dictionary berdasarkan ID kriteria
    dict_bobot = dict(zip(kriteria_cols, bobot_persen))

    # Ekstrak khusus bobot dari kriteria yang dipilih user di awal (fokus_kriteria)
    selected_weights = []
    for crit_id in fokus_kriteria:
        if crit_id in dict_bobot:
            selected_weights.append({
                "id": crit_id,
                "weight": dict_bobot[crit_id]
            })

    # 3. Rekapitulasi Statistik Deskriptif
    stats = {
        "total_analyzed": len(df), # Jumlah total HP dalam CSV setelah difilter harga
        "min_price": int(df['C1'].min()),
        "max_price": int(df['C1'].max()),
        "highest_score": float(df_rank['Nilai_Optimasi_Yi'].max())
    }

    # ==========================================
    # PEMBUATAN DATA UNTUK TAB "PERHITUNGAN"
    # ==========================================
    
    # Kriteria yang aktif / terpilih untuk ditampilkan
    kriteria_labels = [k for k in fokus_kriteria] if fokus_kriteria else kriteria_cols

    # Step 1: Filter Data
    step_1 = df[['Nama_HP', 'C1', 'Brand']].rename(columns={'Nama_HP': 'nama', 'C1': 'harga', 'Brand': 'brand'}).to_dict(orient='records')

    # Step 2: Matriks Keputusan Awal
    matriks_awal = []
    for i, row in df_numeric.iterrows():
        matriks_awal.append({
            "smartphone": row['Nama_HP'],
            "values": [round(val, 2) for val in row[kriteria_cols].values]
        })
    step_2 = {"kriteria": kriteria_cols, "matriks": matriks_awal}

    # Step 3: Normalisasi Matriks
    matriks_norm = []
    for i in range(len(df)):
        matriks_norm.append({
            "smartphone": df.iloc[i]['Nama_HP'],
            # Format ke 4 angka di belakang koma (string) agar rapi seperti desain
            "normalized": [f"{val:.4f}" for val in X_norm_moora[i]]
        })
    step_3 = {
        "formula": "r_ij = x_ij / sqrt(Σ x_ij²)",
        "sample": matriks_norm
    }

    # Step 4: Perhitungan Bobot CRITIC
    std_dev_list = [{"kriteria": k, "stdDev": f"{std_dev[idx]:.4f}"} for idx, k in enumerate(kriteria_cols)]
    weights_list = [{"kriteria": k, "bobot": f"{W_j[idx]*100:.2f}%"} for idx, k in enumerate(kriteria_cols)]
    step_4 = {
        "stdDev": std_dev_list,
        "weights": weights_list,
        "formula": "C_j = σ_j × Σ(1 - r_jk)"
    }

    # Step 5: Perhitungan MOORA
    moora_scores = []
    for i in range(len(df)):
        moora_scores.append({
            "smartphone": df.iloc[i]['Nama_HP'],
            "score": f"{Yi[i]:.4f}"
        })
    step_5 = {
        "formula": "Y_i = Σ(max) w_j × r_ij - Σ(min) w_j × r_ij",
        "scores": moora_scores
    }

    # Step 6: Ranking Final
    ranking_final = []
    for i, row in df_rank.iterrows():
        ranking_final.append({
            "rank": i + 1,
            "smartphone": row['Nama_HP'],
            "score": f"{row['Nilai_Optimasi_Yi']:.4f}"
        })
    step_6 = ranking_final

    # --- UPDATE RETURN JSON ---
    # Kembalikan JSON dengan struktur 3 pilar: recommendations, analysis, dan calculation
    return {
        "recommendations": hasil_rekomendasi,
        "analysis": {
            "weights": dict_bobot,
            "selected_weights": selected_weights,
            "stats": stats
        },
        "calculation": {
            "step_1": step_1,
            "step_2": step_2,
            "step_3": step_3,
            "step_4": step_4,
            "step_5": step_5,
            "step_6": step_6
        }
    }
