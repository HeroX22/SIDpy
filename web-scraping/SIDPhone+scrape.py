import os
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import base64

# Konfigurasi API
API_BASE_URL = "https://demo.sekolahan.id/api"
BEARER_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJzbWstY2FrcmEtbnVzYW50YXJhLnNla29sYWhhbi5pZCIsImF1ZCI6IjEwLjEzMC40Ni41OCIsImlhdCI6MTcwNDYyMDU1NSwibmJmIjoxNzA0NjIwNTY1LCJkYXRhIjp7ImlkIjpudWxsfX0._9Geu5biEBUJ6jf89FtuINcP1rDcPHZ0t9vOAQN1hZk"
HEADERS = {"Authorization": f"Bearer {BEARER_TOKEN}"}

# Fungsi untuk mendapatkan JSON response dari API
def get_json_response(url, method="GET", data=None):
    """Mengambil data JSON dari API dengan metode GET atau POST."""
    if method == "POST":
        response = requests.post(url, headers=HEADERS, data=data)
    else:
        response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        return response.json().get("responseData", {}).get("results", [])
    print(f"Gagal mengambil data dari {url}. Status code: {response.status_code}")
    return None

# Fungsi untuk mencari sekolah
def cari_sekolah():
    """Mencari sekolah berdasarkan nama dan mengembalikan ID sekolah dan subdomain."""
    while True:
        nama_sekolah = input("Masukkan nama sekolah: ")
        sekolah_url = f"{API_BASE_URL}/sekolahdata?namasekolah={nama_sekolah}"
        sekolah_list = get_json_response(sekolah_url)

        if sekolah_list:
            for index, sekolah in enumerate(sekolah_list, start=1):
                print(f"{index}. {sekolah['nama']}")
            try:
                pilihan = int(input("Pilih sekolah (nomor): "))
                id_sekolah = sekolah_list[pilihan - 1]["id"]
                nama_sekolah = sekolah_list[pilihan - 1]["nama"]
                identifier = sekolah_list[pilihan - 1]["identifier"]
                subdomain = base64.b64decode(identifier).decode('utf-8')  # Decode base64 untuk mendapatkan subdomain
                return id_sekolah, nama_sekolah, subdomain
            except (ValueError, IndexError):
                print("Pilihan tidak valid. Coba lagi.")
        else:
            print("Sekolah tidak ditemukan.")

# Fungsi untuk mengambil data kelas
def get_kelas(id_sekolah):
    """Mengambil daftar kelas dari sekolah."""
    kelas_url = f"{API_BASE_URL}/{id_sekolah}/datakelas"
    return get_json_response(kelas_url)

# Fungsi untuk mengambil data siswa dalam kelas
def get_siswa(id_sekolah, kelas_id):
    """Mengambil daftar siswa dalam suatu kelas."""
    siswa_url = f"{API_BASE_URL}/v2/{id_sekolah}/listsiswakelas"
    data_siswa = get_json_response(siswa_url, "POST", {"idkelas": kelas_id, "idsiswa": ""})
    return data_siswa

# Fungsi untuk mengambil profil siswa
def get_profil_siswa(id_sekolah, idsiswa):
    """Mengambil profil siswa berdasarkan ID siswa."""
    profil_url = f"{API_BASE_URL}/v2/{id_sekolah}/profilsiswa"
    return get_json_response(profil_url, "POST", {"idsiswa": idsiswa})

# Fungsi untuk login ke subdomain
def login(subdomain):
    """Login ke subdomain untuk mendapatkan sesi login."""
    login_url = f'https://{subdomain}.sekolahan.id/login/proses'
    main_url = f'https://{subdomain}.sekolahan.id/'
    login_data = {
        'username': 'superadmin',
        'password': 'sigarantang',
        'submit': ''
    }

    session = requests.Session()
    headers = {'User-Agent': 'Mozilla/5.0'}
    session.get(main_url, headers=headers)

    login_response = session.post(login_url, data=login_data, headers=headers)
    if login_response.status_code == 200:
        return session
    print("Login gagal.")
    return None

# Fungsi untuk scrape data siswa
def scrape_siswa(session, subdomain, idsiswa):
    """Scraping data siswa dari halaman edit."""
    data_siswa_url = f'https://{subdomain}.sekolahan.id/datasiswa/edit/{idsiswa}'
    response = session.get(data_siswa_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        fields = ['nama', 'nik', 'no_kk', 'ayah_nik', 'ibu_nik', 'wali_nik', 'no_kip', 'nm_kip', 'no_kps', 'no_kks', 'tglditerima', 'asalsekolah']
        data = {field: get_input_value(soup, field) for field in fields}
        return data
    else:
        print(f"Gagal mengakses halaman siswa, status code: {response.status_code}")
    return {}

# Fungsi untuk mendapatkan nilai input dari form
def get_input_value(soup, field):
    """Mengambil nilai dari input berdasarkan nama field."""
    input_tag = soup.find('input', {'name': field})
    return input_tag['value'] if input_tag else None

# Fungsi untuk menyimpan data siswa ke dalam file terpisah
def simpan_data_siswa(nama_sekolah, kelas, siswa_data, id_sekolah, session, subdomain):
    """Menyimpan data siswa dan profilnya ke dalam file terpisah berdasarkan nama siswa dan kelas."""
    output_folder = os.path.join(os.getcwd(), "Data Sekolah", nama_sekolah, "Data Siswa", kelas)
    os.makedirs(output_folder, exist_ok=True)
    
    for siswa in siswa_data:
        # Mengambil nama siswa dari profil siswa
        profil = get_profil_siswa(id_sekolah, siswa['idsiswa'])
        nama_siswa = profil.get('nama', 'Nama Tidak Ditemukan')
        siswa_folder = os.path.join(output_folder, nama_siswa)
        os.makedirs(siswa_folder, exist_ok=True)
        
        file_name = f"{nama_siswa}.txt"
        output_file_path = os.path.join(siswa_folder, file_name)

        with open(output_file_path, "w") as file:
            file.write(f"=== Data Siswa: {nama_siswa} ===\n")
            file.write(f"ID: {siswa['idsiswa']}\n")
            
            # Cek apakah ada data kelas dalam objek siswa
            if 'kelas' in siswa:
                file.write(f"Kelas: {siswa['kelas']}\n")
            else:
                file.write(f"Kelas: Data Tidak Tersedia\n")
            
            file.write("\n")

            # Mengambil data profil siswa
            tgllahir = profil.get("tgllahir", "")
            password = datetime.strptime(tgllahir, "%Y-%m-%d").strftime("%y%m%d") if tgllahir and tgllahir != '0000-00-00' else "default_password"
            file.write(f"Password: {password}\n")
            
            # Scraping data tambahan dari halaman edit
            scraped_data = scrape_siswa(session, subdomain, siswa['idsiswa'])
            for key, value in {**profil, **scraped_data}.items():
                file.write(f"{key}: {value}\n")
            file.write("\n")
        
        print(f"Data untuk {nama_siswa} berhasil disimpan dalam {file_name}")

# Main Program
def main():
    id_sekolah, nama_sekolah, subdomain = cari_sekolah()
    kelas_list = get_kelas(id_sekolah)
    
    if not kelas_list:
        print("Gagal mendapatkan data kelas.")
        return

    # Login ke subdomain
    session = login(subdomain)
    if session is None:
        return

    for kelas in kelas_list:
        print(f"Mengambil data siswa untuk kelas: {kelas['namakelas']}")
        siswa_list = get_siswa(id_sekolah, kelas["kelasid"])
        
        if siswa_list:
            simpan_data_siswa(nama_sekolah, kelas['namakelas'], siswa_list, id_sekolah, session, subdomain)
            print(f"Data siswa kelas {kelas['namakelas']} berhasil disimpan.")
        else:
            print(f"Tidak ada data siswa di kelas {kelas['namakelas']}")

if __name__ == "__main__":
    main()