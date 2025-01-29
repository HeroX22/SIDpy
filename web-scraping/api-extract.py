import requests
import base64

# Fungsi untuk melakukan dekripsi Base64
def decrypt_base64(encoded_str):
    return base64.b64decode(encoded_str).decode('utf-8')

# Fungsi untuk mengecek koneksi ke URL
def check_url(identifier):
    url = f"https://{identifier}.sekolahan.id/"
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

# Fungsi untuk mengambil data dari API secara dinamis
def fetch_school_data(base_url):
    fetched_ids = set()
    valid_schools = []
    valid_identifiers = []

    # Memulai iterasi dengan query awal dari a-z
    queries = [chr(i) for i in range(97, 123)]  # Query dari "a" hingga "z"

    while queries:
        current_query = queries.pop(0)
        response = requests.get(f"{base_url}?namasekolah={current_query}")

        if response.status_code == 200:
            data = response.json()
            results = data.get("responseData", {}).get("results", [])
            
            # Validasi apakah results adalah daftar
            if not isinstance(results, list):
                print(f"Warning: 'results' is not a list for query '{current_query}'")
                continue

            for result in results:
                school_id = result.get("id")
                school_name = result.get("nama")
                identifier = result.get("identifier")

                if school_id and school_id not in fetched_ids:
                    fetched_ids.add(school_id)

                    # Dekripsi identifier
                    if identifier:
                        decoded_identifier = decrypt_base64(identifier)
                        
                        # Cek koneksi ke URL identifier
                        if check_url(decoded_identifier):
                            valid_schools.append(f"{school_name}")
                            valid_identifiers.append(f"{decoded_identifier}")

            # Jika jumlah hasil mencapai batas (19), coba tambahkan angka/huruf baru
            if len(results) == 19:
                for char in "0123456789":
                    new_query = current_query + char
                    if new_query not in queries:
                        queries.append(new_query)

    return valid_schools, valid_identifiers

# Fungsi utama
if __name__ == "__main__":
    base_url = "https://apiapi.sekolahan.id/api/sekolahdata"

    # Memanggil fungsi untuk fetch data
    school_data, identifier_data = fetch_school_data(base_url)

    # Menyimpan hasil ke file
    with open("valid-nama-sekolah.txt", "w", encoding="utf-8") as school_file:
        school_file.write("\n".join(school_data))

    with open("valid-list-sekolah.txt", "w", encoding="utf-8") as identifier_file:
        identifier_file.write("\n".join(identifier_data))

    print("Data valid berhasil diekstrak dan disimpan ke file valid-nama-sekolah.txt dan valid-list-sekolah.txt")
