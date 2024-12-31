import requests

# URL halaman login
login_url = 'https://smk-cakra-nusantara.sekolahan.id/login/proses'

# Data login: username dan password yang digunakan untuk login
login_data = {
    'username': 'superadmin',  # Ganti dengan username yang sesuai
    'password': 'sigarantang',  # Ganti dengan password yang sesuai
    'submit': ''  # Biasanya tombol submit dikirim dengan parameter 'submit'
}

# Membuat session untuk mempertahankan login
session = requests.Session()

try:
    # Mengirim POST request untuk login
    response = session.post(login_url, data=login_data)

    # Mengecek apakah login berhasil
    if response.status_code == 200 and "berhasil" in response.text:  # Ganti dengan kata kunci yang menunjukkan login berhasil
        print("Login berhasil!")
        # Kamu bisa melanjutkan dengan aksi lain di sini, seperti scraping setelah login berhasil
    else:
        print("Login gagal, periksa username dan password.")
except requests.exceptions.RequestException as e:
    print(f"Terjadi kesalahan saat melakukan request: {e}")
