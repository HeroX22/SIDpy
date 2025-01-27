import requests
from bs4 import BeautifulSoup

# URL halaman login dan URL yang akan di-scrape setelah login
login_url = 'https://smk-cakra-nusantara.sekolahan.id/login/proses'
main_url = 'https://smk-cakra-nusantara.sekolahan.id/'
data_siswa_url = 'https://smk-cakra-nusantara.sekolahan.id/datasiswa/edit/325'
data_guru_url = 'https://smk-cakra-nusantara.sekolahan.id/dataguru'
data_tendik_url = 'https://smk-cakra-nusantara.sekolahan.id/datatendik'
profil_sekolah_url = 'https://smk-cakra-nusantara.sekolahan.id/profilsekolah'

# Data login (username dan password)
login_data = {
    'username': 'superadmin',  # Ganti dengan username yang sesuai
    'password': 'sigarantang',  # Ganti dengan password yang sesuai
    'submit': ''
}

# Header yang digunakan untuk request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
}

# Membuat session untuk mempertahankan login dan cookies
session = requests.Session()

# Langkah 1: Akses halaman awal untuk mendapatkan cookie pertama (PHPSESSID)
initial_response = session.get(main_url, headers=headers)

if 'PHPSESSID' in session.cookies:
    print("Cookie PHPSESSID berhasil didapatkan:", session.cookies['PHPSESSID'])

    # Langkah 2: Login dengan cookie yang didapatkan
    login_response = session.post(login_url, data=login_data, headers=headers)

    if login_response.status_code == 200:
        print("Login berhasil, memeriksa halaman utama...")

        # Fungsi untuk scraping data siswa
        def scrape_siswa():
            response = session.get(data_siswa_url, headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                try:
                    data = {}
                    fields = ['nik', 'no_kk', 'ayah_nik', 'ibu_nik', 'wali_nik', 'no_kip', 'nm_kip', 'no_kps', 'no_kks', 'tglditerima', 'asalsekolah']
                    for field in fields:
                        input_tag = soup.find('input', {'name': field})
                        data[field] = input_tag['value'] if input_tag else 'Tidak ditemukan'

                    for key, value in data.items():
                        print(f"{key}: {value}")
                except Exception as e:
                    print("Error saat scraping data siswa:", e)
            else:
                print(f"Gagal mengakses halaman siswa, status code: {response.status_code}")

        # Fungsi untuk scraping data guru
        def scrape_guru():
            def scrape_page(url):
                response = session.get(url, headers=headers)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    table = soup.find('table', class_='table table-striped table-hover')
                    ids = []
                    if table:
                        rows = table.find('tbody').find_all('tr')
                        for row in rows:
                            cols = row.find_all('td')
                            if len(cols) > 1:
                                id_guru = cols[2].text.strip()
                                ids.append(id_guru)
                    return ids
                else:
                    print(f"Gagal mengakses halaman: {url}, status code: {response.status_code}")
                    return []

            first_page_response = session.get(data_guru_url, headers=headers)
            if first_page_response.status_code == 200:
                soup = BeautifulSoup(first_page_response.text, 'html.parser')
                pagination = soup.find('ul', class_='pagination')
                total_pages = 1
                if pagination:
                    pages = pagination.find_all('a')
                    total_pages = max([int(a.text) for a in pages if a.text.isdigit()])

                print(f"Total halaman: {total_pages}")

                all_ids = []
                for page in range(1, total_pages + 1):
                    page_url = f"{data_guru_url}/?halaman={page}"
                    print(f"Mengakses halaman: {page_url}")
                    all_ids.extend(scrape_page(page_url))

                print("ID Guru yang berhasil di-scrape:")
                for id_guru in all_ids:
                    print(id_guru)
            else:
                print(f"Gagal mengakses halaman guru, status code: {first_page_response.status_code}")

        # Fungsi untuk scraping URL cetak profil tendik
        def scrape_tendik_profiles():
            def scrape_profile_urls(url):
                response = session.get(url, headers=headers)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    table = soup.find('table', class_='table table-striped table-hover')
                    profile_urls = []
                    if table:
                        rows = table.find('tbody').find_all('tr')
                        for row in rows:
                            action_cell = row.find_all('td')[-1]
                            link = action_cell.find('a', href=True, text='Cetak Profil')
                            if link:
                                profile_urls.append(link['href'])
                    return profile_urls
                else:
                    print(f"Gagal mengakses halaman: {url}, status code: {response.status_code}")
                    return []

            # Akses halaman pertama
            first_page_response = session.get(data_tendik_url, headers=headers)
            if first_page_response.status_code == 200:
                first_page_soup = BeautifulSoup(first_page_response.text, 'html.parser')
                
                # Cari elemen pagination
                pagination = first_page_soup.find('ul', class_='pagination')
                total_pages = 1
                if pagination:
                    pages = pagination.find_all('a')
                    page_numbers = [int(a.text) for a in pages if a.text.isdigit()]
                    if page_numbers:
                        total_pages = max(page_numbers)
                    else:
                        print("Tidak ditemukan nomor halaman pada elemen pagination. Asumsikan hanya satu halaman.")
                else:
                    print("Elemen pagination tidak ditemukan. Asumsikan hanya satu halaman.")

                print(f"Total halaman: {total_pages}")

                # Iterasi semua halaman untuk scraping profil tendik
                all_profile_urls = []
                for page in range(1, total_pages + 1):
                    page_url = f"{data_tendik_url}/?halaman={page}"
                    print(f"Mengakses halaman: {page_url}")
                    all_profile_urls.extend(scrape_profile_urls(page_url))

                # Menampilkan URL profil tendik
                print("URL Cetak Profil Tendik yang berhasil di-scrape:")
                for profile_url in all_profile_urls:
                    print(profile_url)
            else:
                print(f"Gagal mengakses halaman pertama data tendik, status code: {first_page_response.status_code}")

            # Akses halaman pertama
            first_page_response = session.get(data_tendik_url, headers=headers)
            if first_page_response.status_code == 200:
                first_page_soup = BeautifulSoup(first_page_response.text, 'html.parser')
                
                # Cari elemen pagination
                pagination = first_page_soup.find('ul', class_='pagination')
                total_pages = 1
                if pagination:
                    pages = pagination.find_all('a')
                    page_numbers = [int(a.text) for a in pages if a.text.isdigit()]
                    if page_numbers:
                        total_pages = max(page_numbers)
                    else:
                        print("Tidak ditemukan nomor halaman pada elemen pagination. Asumsikan hanya satu halaman.")
                else:
                    print("Elemen pagination tidak ditemukan. Asumsikan hanya satu halaman.")

                print(f"Total halaman: {total_pages}")

                # Iterasi semua halaman untuk scraping profil tendik
                all_profile_urls = []
                for page in range(1, total_pages + 1):
                    page_url = f"{data_tendik_url}/?halaman={page}"
                    print(f"Mengakses halaman: {page_url}")
                    profile_urls = scrape_profile_urls(page_url)
                    all_profile_urls.extend(profile_urls)

                # Menampilkan URL profil tendik
                print("URL Cetak Profil Tendik yang berhasil di-scrape:")
                for profile_url in all_profile_urls:
                    print(profile_url)
            else:
                print(f"Gagal mengakses halaman pertama data tendik, status code: {first_page_response.status_code}")

            def scrape_profile_urls(url):
                response = session.get(url, headers=headers)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    table = soup.find('table', class_='table table-striped table-hover')
                    profile_urls = []
                    if table:
                        rows = table.find('tbody').find_all('tr')
                        for row in rows:
                            action_cell = row.find_all('td')[-1]
                            link = action_cell.find('a', href=True, text='Cetak Profil')
                            if link:
                                profile_urls.append(link['href'])
                    return profile_urls
                else:
                    print(f"Gagal mengakses halaman: {url}, status code: {response.status_code}")
                    return []

            first_page_response = session.get(data_tendik_url, headers=headers)
            if first_page_response.status_code == 200:
                first_page_soup = BeautifulSoup(first_page_response.text, 'html.parser')
                pagination = first_page_soup.find('ul', class_='pagination')
                total_pages = 1
                if pagination:
                    pages = pagination.find_all('a')
                    page_numbers = [int(a.text) for a in pages if a.text.isdigit()]
                    if page_numbers:
                        total_pages = max(page_numbers)
                    else:
                        print("Tidak ditemukan nomor halaman pada elemen pagination.")
                else:
                    print("Elemen pagination tidak ditemukan. Asumsikan hanya satu halaman.")


                print(f"Total halaman: {total_pages}")

                all_profile_urls = []
                for page in range(1, total_pages + 1):
                    page_url = f"{data_tendik_url}/?halaman={page}"
                    print(f"Mengakses halaman: {page_url}")
                    all_profile_urls.extend(scrape_profile_urls(page_url))

                print("URL Cetak Profil yang berhasil di-scrape:")
                for profile_url in all_profile_urls:
                    print(profile_url)
            else:
                print(f"Gagal mengakses halaman pertama data tendik, status code: {first_page_response.status_code}")

        # Fungsi untuk scraping profil sekolah
        def scrape_profil_sekolah():
            response = session.get(profil_sekolah_url, headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                def get_input_value(name):
                    input_tag = soup.find('input', {'name': name})
                    return input_tag['value'] if input_tag else 'Tidak ditemukan'

                # Profil Sekolah
                nama_sekolah = get_input_value('pnamasekolah')
                nss = get_input_value('nsssekolah')
                npsn = get_input_value('npsnsekolah')
                alamat = get_input_value('alamat_sekolah')
                kode_pos = get_input_value('kode_possekolah')
                desa_kelurahan = get_input_value('desa_kelurahansekolah')
                kecamatan = get_input_value('kecamatan_sekolah')
                kabupaten_kota = get_input_value('kabupatenkota_sekolah')
                provinsi = get_input_value('provinsi_sekolah')

                print("\n=== Profil Sekolah ===")
                print(f'Nama Sekolah: {nama_sekolah}')
                print(f'NSS: {nss}')
                print(f'NPSN: {npsn}')
                print(f'Alamat: {alamat}')
                print(f'Kode Pos: {kode_pos}')
                print(f'Desa/Kelurahan: {desa_kelurahan}')
                print(f'Kecamatan: {kecamatan}')
                print(f'Kabupaten/Kota: {kabupaten_kota}')
                print(f'Provinsi: {provinsi}')
            else:
                print(f"Gagal mengakses halaman profil sekolah, status code: {response.status_code}")

        # Panggil fungsi scraping
        scrape_siswa()
        scrape_guru()
        scrape_tendik_profiles()
        scrape_profil_sekolah()

    else:
        print("Login gagal, status code:", login_response.status_code)
else:
    print("Gagal mendapatkan cookie PHPSESSID dari halaman awal.")