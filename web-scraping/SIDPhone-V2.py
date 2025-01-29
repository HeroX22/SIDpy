import os
import requests
from datetime import datetime

# Konfigurasi API
API_BASE_URL = "https://demo.sekolahan.id/api"
BEARER_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJzbWstY2FrcmEtbnVzYW50YXJhLnNla29sYWhhbi5pZCIsImF1ZCI6IjEwLjEzMC40Ni41OCIsImlhdCI6MTcwNDYyMDU1NSwibmJmIjoxNzA0NjIwNTY1LCJkYXRhIjp7ImlkIjpudWxsfX0._9Geu5biEBUJ6jf89FtuINcP1rDcPHZ0t9vOAQN1hZk"
HEADERS = {"Authorization": f"Bearer {BEARER_TOKEN}"}

def get_json_response(url, method="GET", data=None):
    """Mengambil data JSON dari API dengan metode GET atau POST."""
    if method == "POST":
        response = requests.post(url, headers=HEADERS, data=data)  # Menggunakan data=form-data sesuai kode lama
    else:
        response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        return response.json().get("responseData", {}).get("results", [])
    print(f"Gagal mengambil data dari {url}. Status code: {response.status_code}")
    return None

def cari_sekolah():
    """Mencari sekolah berdasarkan nama dan mengembalikan ID sekolah."""
    while True:
        nama_sekolah = input("Masukkan nama sekolah: ")
        sekolah_url = f"{API_BASE_URL}/sekolahdata?namasekolah={nama_sekolah}"
        sekolah_list = get_json_response(sekolah_url)

        if sekolah_list:
            for index, sekolah in enumerate(sekolah_list, start=1):
                print(f"{index}. {sekolah['nama']}")
            try:
                pilihan = int(input("Pilih sekolah (nomor): "))
                return sekolah_list[pilihan - 1]["id"], sekolah_list[pilihan - 1]["nama"]
            except (ValueError, IndexError):
                print("Pilihan tidak valid. Coba lagi.")
        else:
            print("Sekolah tidak ditemukan.")

def get_kelas(id_sekolah):
    """Mengambil daftar kelas dari sekolah."""
    kelas_url = f"{API_BASE_URL}/{id_sekolah}/datakelas"
    return get_json_response(kelas_url)

def get_siswa(id_sekolah, kelas_id):
    """Mengambil daftar siswa dalam suatu kelas."""
    siswa_url = f"{API_BASE_URL}/v2/{id_sekolah}/listsiswakelas"
    data_siswa = get_json_response(siswa_url, "POST", {"idkelas": kelas_id, "idsiswa": ""})  # Sesuai dengan kode lama
    return data_siswa

def get_profil_siswa(id_sekolah, idsiswa):
    """Mengambil profil siswa berdasarkan ID."""
    profil_url = f"{API_BASE_URL}/v2/{id_sekolah}/profilsiswa"
    return get_json_response(profil_url, "POST", {"idsiswa": idsiswa})

def simpan_data_siswa(nama_sekolah, nama_kelas, data_siswa, id_sekolah):
    """Menyimpan data siswa dan profilnya ke dalam file."""
    output_folder = os.path.join(os.getcwd(), "Data Siswa", nama_sekolah)
    os.makedirs(output_folder, exist_ok=True)
    output_file_path = os.path.join(output_folder, f"{nama_kelas}.txt")

    with open(output_file_path, "w") as file:
        file.write(f"=== Data Siswa {nama_kelas} ===\n")
        file.write(f"Total Siswa: {len(data_siswa)}\n\n")
        
        for siswa in data_siswa:
            profil = get_profil_siswa(id_sekolah, siswa['idsiswa'])
            tgllahir = profil.get("tgllahir", "")
            password = datetime.strptime(tgllahir, "%Y-%m-%d").strftime("%y%m%d") if tgllahir and tgllahir != '0000-00-00' else "default_password"
            
            file.write(f"=== Profil Siswa ===\nID: {siswa['idsiswa']}\nPassword: {password}\n")
            for key, value in profil.items():
                file.write(f"{key}: {value}\n")
            file.write("\n")

def main():
    print("1. Masukkan ID Sekolah")
    print("2. Cari Sekolah")
    pilihan = input("Pilih opsi (1/2): ")

    if pilihan == "1":
        id_sekolah = input("Masukkan ID Sekolah: ")
        nama_sekolah = "Unknown"
    elif pilihan == "2":
        id_sekolah, nama_sekolah = cari_sekolah()
    else:
        print("Opsi tidak valid. Program berhenti.")
        return

    kelas_list = get_kelas(id_sekolah)
    if not kelas_list:
        print("Gagal mendapatkan data kelas.")
        return

    for kelas in kelas_list:
        print(f"Mengambil data siswa untuk kelas: {kelas['namakelas']}")
        siswa_list = get_siswa(id_sekolah, kelas["kelasid"])
        if siswa_list:
            simpan_data_siswa(nama_sekolah, kelas['namakelas'], siswa_list, id_sekolah)
            print(f"Data siswa kelas {kelas['namakelas']} berhasil disimpan.")
        else:
            print(f"Tidak ada data siswa di kelas {kelas['namakelas']}")

if __name__ == "__main__":
    main()
