import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import datetime

# --------------------------------------------
# 1. Muat dataset harian dan per-jam
# --------------------------------------------
df_harian = pd.read_csv('data/day.csv')
df_per_jam = pd.read_csv('data/hour.csv')

# Ubah kolom tanggal ('dteday') menjadi tipe datetime
df_harian['dteday'] = pd.to_datetime(df_harian['dteday'])

# --------------------------------------------
# 2. Judul Aplikasi Streamlit
# --------------------------------------------
st.title("Dashboard Analisis Penyewaan Sepeda")

# --------------------------------------------
# 3. Menu Pilihan Visualisasi di Sidebar
# --------------------------------------------
st.sidebar.header("Visualisasi yang Tersedia")
pilihan_grafik = st.sidebar.selectbox(
    "Silakan pilih tipe grafik:",
    [
        "Distribusi Penyewaan Sepeda",
        "Tren Harian & Bulanan",
        "Pola Berdasarkan Cuaca",
        "Clustering"
    ]
)

# --------------------------------------------
# 4. Filter Interaktif di Sidebar
# --------------------------------------------
st.sidebar.header("Filter Data")

# Opsi musim (dengan tambahan pilihan "Semua Musim")
opsi_musim = ['Semua Musim'] + list(df_harian['season'].unique())
# Opsi kondisi cuaca (dengan tambahan pilihan "Semua Cuaca")
opsi_cuaca = ['Semua Cuaca'] + list(df_harian['weathersit'].unique())

# Dropdown untuk memilih musim
filter_musim = st.sidebar.selectbox("Pilih Musim:", opsi_musim, key="pilih_musim")
# Dropdown untuk memilih kondisi cuaca
filter_cuaca = st.sidebar.selectbox("Pilih Cuaca:", opsi_cuaca, key="pilih_cuaca")

# --------------------------------------------
# 5. Filter Berdasarkan Rentang Tanggal
# --------------------------------------------
# Tentukan batas terendah dan tertinggi tanggal pada data
tanggal_min = df_harian['dteday'].min().date()
tanggal_maks = df_harian['dteday'].max().date()

# Opsi pemilihan tanggal awal dan akhir
tanggal_awal = st.sidebar.date_input("Mulai Tanggal:", tanggal_min, key="picker_tanggal_awal")
tanggal_akhir = st.sidebar.date_input("Sampai Tanggal:", tanggal_maks, key="picker_tanggal_akhir")

# Validasi: jika tanggal_awal > tanggal_akhir, tampilkan pesan error
if tanggal_awal > tanggal_akhir:
    st.sidebar.error("⛔ Tanggal awal tidak boleh setelah tanggal akhir!")

# Ubah kembali ke tipe datetime untuk difilter
tanggal_awal = pd.to_datetime(tanggal_awal)
tanggal_akhir = pd.to_datetime(tanggal_akhir)

# --------------------------------------------
# 6. Proses Filtering Data
# --------------------------------------------
# Ambil data di antara tanggal_awal dan tanggal_akhir
df_terfilter = df_harian[
    (df_harian['dteday'] >= tanggal_awal) &
    (df_harian['dteday'] <= tanggal_akhir)
]

# Jika dipilih musim tertentu (bukan "Semua Musim"), saring lagi
if filter_musim != 'Semua Musim':
    df_terfilter = df_terfilter[df_terfilter['season'] == filter_musim]

# Jika dipilih cuaca tertentu (bukan "Semua Cuaca"), saring lagi
if filter_cuaca != 'Semua Cuaca':
    df_terfilter = df_terfilter[df_terfilter['weathersit'] == filter_cuaca]

# Jika hasil filter kosong, tampilkan peringatan; jika tidak, tampilkan potongan data
if df_terfilter.empty:
    st.warning("⚠️ Tidak ada data sesuai dengan filter yang dipilih.")
else:
    st.header("Data Setelah Proses Filtering")
    st.write(df_terfilter.head())

# --------------------------------------------
# 7. Pilihan Visualisasi Berdasarkan menu
# --------------------------------------------
# 7.a. Distribusi Jumlah Penyewaan Sepeda
if pilihan_grafik == "Distribusi Penyewaan Sepeda":
    st.subheader("Distribusi Jumlah Penyewaan Sepeda (Harian)")
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.histplot(
        df_terfilter['cnt'],
        bins=30,
        kde=True,
        color='green',
        ax=ax
    )
    ax.set_title("Distribusi Jumlah Penyewaan Sepeda per Hari")
    ax.set_xlabel("Jumlah Penyewaan")
    ax.set_ylabel("Frekuensi")
    st.pyplot(fig)

# 7.b. Tren Harian & Tren Bulanan
elif pilihan_grafik == "Tren Harian & Bulanan":
    st.subheader("Tren Penyewaan Sepeda Berdasarkan Waktu Harian (Jam)")

    # Ambil kolom numerik dari df_per_jam, lalu hitung rata-rata 'cnt' per jam (hr)
    df_jam_numerik = df_per_jam.select_dtypes(include=['number'])
    rata_per_jam = df_jam_numerik.groupby('hr').mean().reset_index()

    fig, ax = plt.subplots(figsize=(12, 5))
    sns.lineplot(
        x='hr',
        y='cnt',
        data=rata_per_jam,
        marker='o',
        color='purple',
        ax=ax
    )
    ax.set_title("Rata-Rata Penyewaan per Jam")
    ax.set_xlabel("Jam (0–23)")
    ax.set_ylabel("Rata-rata Penyewaan")
    st.pyplot(fig)


    # Perbandingan Hari Kerja vs Akhir Pekan berdasarkan jam
    st.subheader("Perbandingan Hari Kerja dan Akhir Pekan Berdasarkan Jam")
    kolom_numerik = df_per_jam.select_dtypes(include='number').columns
    df_hr_work = df_per_jam.groupby(['hr', 'workingday'], as_index=False)[kolom_numerik].mean()

    fig, ax = plt.subplots(figsize=(12, 5))
    sns.lineplot(
        x='hr',
        y='cnt',
        hue='workingday',
        data=df_hr_work,
        marker='o',
        ax=ax
    )
    ax.set_title("Perbandingan Penyewaan Sepeda: Hari Kerja vs Akhir Pekan")
    ax.set_xlabel("Jam")
    ax.set_ylabel("Jumlah Penyewaan Sepeda")
    ax.legend(title='Hari Kerja', labels=['Akhir Pekan', 'Hari Kerja'])
    ax.grid(True)
    st.pyplot(fig)

    # Hitung rata-rata 'cnt' per bulan (mnth) dari df_harian
    st.subheader("Tren Penyewaan Sepeda Berdasarkan Waktu Bulanan")
    rata_per_bulan = df_harian.groupby('mnth').mean().reset_index()
    
    fig, ax = plt.subplots(figsize=(12, 5))
    sns.lineplot(
        x='mnth',
        y='cnt',
        data=rata_per_bulan,
        marker='o',
        color='orange',
        ax=ax
    )
    ax.set_title("Tren Penyewaan Sepeda per Bulan")
    ax.set_xlabel("Bulan (1–12)")
    ax.set_ylabel("Rata-rata Penyewaan")
    st.pyplot(fig)

# 7.c. Pola Berdasarkan Kondisi Cuaca
elif pilihan_grafik == "Pola Berdasarkan Cuaca":
    st.subheader("Pengaruh Cuaca, Suhu, dan Kecepatan Angin terhadap Jumlah Penyewaan")

    st.write("Jumlah data setelah filter:", df_terfilter.shape)

    if df_terfilter.empty:
        st.warning("❌ Data kosong setelah filter. Ubah pilihan musim/cuaca.")
    else:
        # Pastikan 'weathersit' dalam bentuk string
        df_terfilter['weathersit'] = df_terfilter['weathersit'].astype(str)

        # --- Boxplot Cuaca vs Penyewaan ---
        fig1 = plt.figure(figsize=(12, 6))
        sns.boxplot(x='weathersit', y='cnt', data=df_terfilter, palette='coolwarm')
        plt.title("Pengaruh Cuaca terhadap Jumlah Penyewaan Sepeda")
        plt.xlabel("Kondisi Cuaca (1=Cerah, 2=Mendung, 3=Hujan)")
        plt.ylabel("Jumlah Penyewaan Sepeda")
        st.pyplot(fig1)

        # --- Regresi Suhu vs Penyewaan ---
        fig2 = plt.figure(figsize=(12, 5))
        sns.regplot(
            x='temp',
            y='cnt',
            data=df_terfilter,
            scatter_kws={'alpha': 0.7},
            line_kws={'color': 'red'}
        )
        plt.title("Hubungan Suhu dengan Jumlah Penyewaan Sepeda")
        plt.xlabel("Suhu Normalisasi")
        plt.ylabel("Jumlah Penyewaan Sepeda")
        st.pyplot(fig2)

        # --- Regresi Kecepatan Angin vs Penyewaan ---
        fig3 = plt.figure(figsize=(12, 6))
        sns.regplot(
            x='windspeed',
            y='cnt',
            data=df_terfilter,
            scatter_kws={'alpha': 0.7},
            line_kws={'color': 'blue'}
        )
        plt.title("Hubungan Kecepatan Angin dengan Jumlah Penyewaan Sepeda")
        plt.xlabel("Kecepatan Angin")
        plt.ylabel("Jumlah Penyewaan Sepeda")
        st.pyplot(fig3)



# 7.d. Clustering (Sederhana dengan Kategori Waktu)
elif pilihan_grafik == "Clustering":
    st.subheader("Clustering: Pola Penggunaan Berdasarkan Waktu dan Jumlah Penyewaan")

    # Clustering Manual: Kategori waktu dalam sehari
    bins = [0, 6, 12, 18, 24]
    labels = ['Malam', 'Pagi', 'Siang', 'Sore']
    df_per_jam['time_of_day'] = pd.cut(df_per_jam['hr'], bins=bins, labels=labels, right=False)

    # Visualisasi boxplot waktu dalam sehari
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.boxplot(x='time_of_day', y='cnt', data=df_per_jam, palette='coolwarm', ax=ax)
    ax.set_title("Pola Penyewaan Sepeda Berdasarkan Waktu dalam Sehari")
    ax.set_xlabel("Waktu dalam Sehari")
    ax.set_ylabel("Jumlah Penyewaan Sepeda")
    st.pyplot(fig)

    # Clustering Manual: Kategori jumlah penyewaan
    cnt_bins = [0, 100, 300, 600]
    cnt_labels = ['Rendah', 'Sedang', 'Tinggi']
    df_per_jam['cnt_category'] = pd.cut(df_per_jam['cnt'], bins=cnt_bins, labels=cnt_labels, right=False)

    # Visualisasi distribusi kategori jumlah penyewaan
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.countplot(x='cnt_category', data=df_per_jam, palette='coolwarm', ax=ax)
    ax.set_title("Distribusi Kategori Jumlah Penyewaan Sepeda")
    ax.set_xlabel("Kategori Penyewaan")
    ax.set_ylabel("Frekuensi")
    st.pyplot(fig)

    st.write("""
    **Wawasan Clustering:**
    - Pagi dan sore hari menunjukkan puncak penyewaan tertinggi.
    - Jam malam (00–06) cenderung paling sepi.
    - Saran strategi: Diskon khusus jam malam atau tambahan armada pada jam sibuk.
    """)


# 8. Footer/Info Pembuat di Sidebar
st.sidebar.text("Dashboard by Jaya Saputra")
