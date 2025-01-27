import requests

ListSchools = "../list-sekolah.txt"

with open(ListSchools, 'r') as schools:
    for school in schools:
        filter = school.strip()
        url = f"https://{filter}.sekolahan.id"
        #print(url)

        try:
            test = requests.get(url)
            # print(f"{url}:{test.status_code}")
            if test.status_code == 200:
                # with open('active.txt', 'a') as file:
                #     file.write(url + "\n")
                print(f"{url}:{test.status_code} (active)")
            # else:
            #     with open('inactive.txt', 'a') as infile:
            #         infile.write(url + "\n")
            #     print(f"{url}:{test.status_code} (inactive)")
        except requests.exceptions.RequestException as error:
            print(f"{url}: Error")