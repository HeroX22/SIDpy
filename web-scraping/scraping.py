import requests
from bs4 import BeautifulSoup

# URL halaman login dan URL yang akan di-scrape setelah login
LOGIN_URL = 'https://smk-pertiwi-kuningan.sekolahan.id/login/proses'
MAIN_URL = 'https://smk-pertiwi-kuningan.sekolahan.id/'
DATA_SISWA_URL = 'https://smk-pertiwi-kuningan.sekolahan.id/datasiswa/edit/325'
DATA_GURU_URL = 'https://smk-pertiwi-kuningan.sekolahan.id/dataguru'
DATA_TENDIK_URL = 'https://smk-pertiwi-kuningan.sekolahan.id/datatendik'
PROFIL_SEKOLAH_URL = 'https://smk-pertiwi-kuningan.sekolahan.id/profilsekolah'

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


def get_cookie():
    """Mendapatkan cookie PHPSESSID dari halaman awal."""
    response = session.get(MAIN_URL, headers=headers)
    if 'PHPSESSID' in session.cookies:
        print(f"Cookie PHPSESSID berhasil didapatkan: {session.cookies['PHPSESSID']}")
        return True
    print("Gagal mendapatkan cookie PHPSESSID dari halaman awal.")
    return False


def login():
    """Melakukan login menggunakan session dan cookie."""
    response = session.post(LOGIN_URL, data=login_data, headers=headers)
    if response.status_code == 200:
        print("Login berhasil.")
        return True
    print(f"Login gagal, status code: {response.status_code}")
    return False


def get_input_value(soup, name):
    """Mengambil nilai input dari halaman menggunakan BeautifulSoup."""
    input_tag = soup.find('input', {'name': name})
    return input_tag['value'] if input_tag else 'Tidak ditemukan'


def scrape_siswa():
    """Scraping data siswa."""
    response = session.get(DATA_SISWA_URL, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        fields = ['nik', 'no_kk', 'ayah_nik', 'ibu_nik', 'wali_nik', 'no_kip', 'nm_kip', 'no_kps', 'no_kks', 'tglditerima', 'asalsekolah']
        data = {field: get_input_value(soup, field) for field in fields}
        for key, value in data.items():
            print(f"{key}: {value}")
    else:
        print(f"Gagal mengakses halaman siswa, status code: {response.status_code}")


def scrape_guru():
    """Scraping data guru."""
    def scrape_page(url):
        response = session.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', class_='table table-striped table-hover')
            if table:
                rows = table.find('tbody').find_all('tr')
                # Mengambil ID dan Nama dari setiap baris
                guru_data = []
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) > 1:
                        # Mengambil ID dari kolom ketiga
                        id_guru = cols[2].text.strip()
                        # Nama ada di dalam tag <strong> atau di dalam <td> jika tidak ada <strong>
                        nama_guru = cols[3].find('strong')
                        if nama_guru:
                            nama_guru = nama_guru.text.strip()
                        else:
                            nama_guru = cols[3].text.strip()
                        guru_data.append((id_guru, nama_guru))
                return guru_data
        print(f"Gagal mengakses halaman: {url}, status code: {response.status_code}")
        return []

    first_page_response = session.get(DATA_GURU_URL, headers=headers)
    if first_page_response.status_code == 200:
        soup = BeautifulSoup(first_page_response.text, 'html.parser')
        pagination = soup.find('ul', class_='pagination')
        total_pages = max([int(a.text) for a in pagination.find_all('a') if a.text.isdigit()], default=1)

        print(f"Total halaman: {total_pages}")

        all_guru_data = []
        for page in range(1, total_pages + 1):
            page_url = f"{DATA_GURU_URL}/?halaman={page}"
            print(f"Mengakses halaman: {page_url}")
            all_guru_data.extend(scrape_page(page_url))

        # Menampilkan ID dan Nama guru yang berhasil di-scrape
        print("ID dan Nama Guru yang berhasil di-scrape:")
        for id_guru, nama_guru in all_guru_data:
            print(f"ID: {id_guru}, Nama: {nama_guru}")
    else:
        print(f"Gagal mengakses halaman guru, status code: {first_page_response.status_code}")


def scrape_tendik_profiles():
    """Scraping profil tendik."""
    def scrape_profile_urls(url):
        response = session.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', class_='table table-striped table-hover')
            if table:
                return [row.find_all('td')[-1].find('a', href=True, string='Cetak Profil')['href'] for row in table.find('tbody').find_all('tr') if row.find_all('td')]
        print(f"Gagal mengakses halaman: {url}, status code: {response.status_code}")
        return []

    first_page_response = session.get(DATA_TENDIK_URL, headers=headers)
    if first_page_response.status_code == 200:
        soup = BeautifulSoup(first_page_response.text, 'html.parser')
        pagination = soup.find('ul', class_='pagination')
        total_pages = max([int(a.text) for a in pagination.find_all('a') if a.text.isdigit()], default=1)

        print(f"Total halaman: {total_pages}")

        all_profile_urls = []
        for page in range(1, total_pages + 1):
            page_url = f"{DATA_TENDIK_URL}/?halaman={page}"
            print(f"Mengakses halaman: {page_url}")
            all_profile_urls.extend(scrape_profile_urls(page_url))

        print("URL Cetak Profil Tendik yang berhasil di-scrape:")
        for profile_url in all_profile_urls:
            print(profile_url)
    else:
        print(f"Gagal mengakses halaman pertama data tendik, status code: {first_page_response.status_code}")


def scrape_profil_sekolah():
    """Scraping profil sekolah."""
    response = session.get(PROFIL_SEKOLAH_URL, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Profil Sekolah
        nama_sekolah = get_input_value(soup, 'pnamasekolah')
        nss = get_input_value(soup, 'nsssekolah')
        npsn = get_input_value(soup, 'npsnsekolah')
        alamat = get_input_value(soup, 'alamat_sekolah')
        kode_pos = get_input_value(soup, 'kode_possekolah')
        desa_kelurahan = get_input_value(soup, 'desa_kelurahansekolah')
        kecamatan = get_input_value(soup, 'kecamatan_sekolah')
        kabupaten_kota = get_input_value(soup, 'kabupatenkota_sekolah')
        provinsi = get_input_value(soup, 'provinsi_sekolah')
        latitude = get_input_value(soup, 'latitude')
        longitude = get_input_value(soup, 'longitude')

        # Informasi Sekolah
        nomor_telepon = get_input_value(soup, 'nomor_teleponsekolah')
        nomor_fax = get_input_value(soup, 'nomor_faxsekolah')
        email = get_input_value(soup, 'emailsekolah')
        website = get_input_value(soup, 'websitesekolah')
        status_kepemilikan = soup.find('select', {'name': 'status_pemilik'}).find('option', selected=True).text if soup.find('select', {'name': 'status_pemilik'}) else 'Tidak ditemukan'

        # Kelengkapan Sekolah
        sk_pendirian = get_input_value(soup, 'sk_pendirian_sekolah')
        tgl_sk_pendirian = get_input_value(soup, 'tgl_sk_pendirian_sekolah')
        sk_izin_operasional = get_input_value(soup, 'sk_izin_operasional')
        tgl_sk_izin_operasional = get_input_value(soup, 'tgl_sk_izin_operasional')
        no_rekening = get_input_value(soup, 'no_rekeningsekolah')
        nama_bank = get_input_value(soup, 'nama_banksekolah')
        rekening_atas_nama = get_input_value(soup, 'rekening_atas_nama')

        # Profile Yayasan
        nama_yayasan = get_input_value(soup, 'namayayasan')
        pimpinan_yayasan = get_input_value(soup, 'nama_pimpinan_yayasan')
        alamat_yayasan = get_input_value(soup, 'alamat_yayasan')
        kode_pos_yayasan = get_input_value(soup, 'kode_posyayasan')
        desa_kelurahan_yayasan = get_input_value(soup, 'desa_kelurahanyayasan')
        sk_pendirian_yayasan = get_input_value(soup, 'sk_pendirian_yayasan')
        tgl_sk_pendirian_yayasan = get_input_value(soup, 'tgl_sk_pendirian_yayasan')

        # Menampilkan hasil scraping
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
        print(f'Latitude: {latitude}')
        print(f'Longitude: {longitude}')

        print("\n=== Informasi Sekolah ===")
        print(f'Nomor Telepon: {nomor_telepon}')
        print(f'Nomor Fax: {nomor_fax}')
        print(f'Email: {email}')
        print(f'Website: {website}')
        print(f'Status Kepemilikan: {status_kepemilikan}')

        print("\n=== Kelengkapan Sekolah ===")
        print(f'Nomor SK/Izin Pendirian: {sk_pendirian}')
        print(f'Tanggal SK/Izin Pendirian: {tgl_sk_pendirian}')
        print(f'Nomor SK Izin Operasional: {sk_izin_operasional}')
        print(f'Tanggal SK Izin Operasional: {tgl_sk_izin_operasional}')
        print(f'Nomor Rekening Bank: {no_rekening}')
        print(f'Nama Bank: {nama_bank}')
        print(f'Rekening Atas Nama: {rekening_atas_nama}')

        print("\n=== Profile Yayasan ===")
        print(f'Nama Yayasan: {nama_yayasan}')
        print(f'Pimpinan Yayasan: {pimpinan_yayasan}')
        print(f'Alamat Yayasan: {alamat_yayasan}')
        print(f'Kode Pos Yayasan: {kode_pos_yayasan}')
        print(f'Desa/Kelurahan Yayasan: {desa_kelurahan_yayasan}')
        print(f'Nomor Akte Pendirian Yayasan: {sk_pendirian_yayasan}')
        print(f'Tanggal Akte Pendirian Yayasan: {tgl_sk_pendirian_yayasan}')
    else:
        print(f"Gagal mengakses halaman profil sekolah, status code: {response.status_code}")


def main():
    """Fungsi utama untuk menjalankan semua proses."""
    if get_cookie() and login():
        scrape_siswa()
        scrape_guru()
        scrape_tendik_profiles()
        scrape_profil_sekolah()


if __name__ == '__main__':
    main()
