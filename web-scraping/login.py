import requests

# URL halaman login
login_url = 'https://smk-cakra-nusantara.sekolahan.id/login/proses'
main_url = 'https://smk-cakra-nusantara.sekolahan.id/'

# Data login (username dan password)
login_data = {
    'username': 'superadmin',  # Ganti dengan username yang sesuai
    'password': 'sigarantang',  # Ganti dengan password yang sesuai
    'submit': ''  # Tombol submit biasanya dikirim dengan parameter 'submit'
}

# Header yang digunakan untuk request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
}

# Membuat session untuk mempertahankan login dan cookies
session = requests.Session()

# Langkah 1: Akses halaman awal untuk mendapatkan cookie pertama (PHPSESSID)
initial_response = session.get(main_url, headers=headers)

# Mengecek apakah cookie pertama berhasil didapatkan
if 'PHPSESSID' in session.cookies:
    print("Cookie PHPSESSID berhasil didapatkan:", session.cookies['PHPSESSID'])
    
    # Langkah 2: Login dengan cookie yang didapatkan
    login_response = session.post(login_url, data=login_data, headers=headers)

    if login_response.status_code == 200:
        print("Login berhasil, memeriksa halaman utama...")
        
        # Langkah 3: Akses halaman utama setelah login untuk memastikan login berhasil
        main_response = session.get(main_url, headers=headers)
        
        # Mengecek apakah halaman utama mengandung teks "super admin"
        if "super admin" in main_response.text.lower():  # Menggunakan .lower() untuk case-insensitive
            print("Login berhasil!")
        else:
            print("Login gagal, tidak ditemukan 'super admin' di halaman utama.")
    else:
        print("Login gagal, status code:", login_response.status_code)
else:
    print("Gagal mendapatkan cookie PHPSESSID dari halaman awal.")
