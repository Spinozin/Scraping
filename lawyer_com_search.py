from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from docx import Document
from collections import OrderedDict
import os, csv, re, json

lawyers_com = f"https://www.lawyers.com/all-legal-issues/{city}/{state}/law-firms{pg}/?={category}"

state_abbrs = OrderedDict(zip(state_abbs.values(), state_abbs.keys()))

default_path = os.chdir('/Users/RavneetKapoor/Desktop/qrtools/attsearch/csv_files')

#t_states = t_state_cities.keys()

fl = open("../us_states_cities.json")
fl = fl.read()
states_cities = json.loads(fl)

states = list(states_cities.keys())[3:7]

t_categories = [
    "Appeals"
]

def mk_rqst(lnk):
    req = Request(lnk, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    return BeautifulSoup(webpage, 'lxml')

def get_phone_num(contact):
    try:
        phone = next(contact.find("a", {"class": "opt-d-phone"}).stripped_strings)
        if phone == "View Phone #":
            try:
                phone = contact.find("li", {"class":"srl-phone"}).a.attrs["data-phonenum"]
            except:
                print("Not there *******************************************************")
    except:
        print("Not there *******************************************************")
    return phone


# in csv_files directory

def mkfiles(arr_states, dct, dflt_pth):
    with open("totals_for_each_state.csv", mode="w") as stt_ttl_sheet:
        stt_writer = csv.writer(stt_ttl_sheet, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        stt_writer.writerow(["State", "Total"])
        for state in arr_states:
            try:
                stt_ttl = 0
                os.makedirs(f"{state}")
                os.chdir(f"{state}")
                # location: ... attsearch/csv_files/{state}
                with open(f"totals_for_each_city.csv", mode="w") as city_ttl_sheet:
                    city_writer = csv.writer(city_ttl_sheet, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    city_writer.writerow(["City", "Total"])
                    print(f"State: {state}"*10)
                    if len(state.split(" ")) > 1: state_lnk = "-".join(state.lower().split(" "))
                    else: state_lnk = state.lower()
                    for city in dct[state]:
                        os.makedirs(f"{city}")
                        print(f"City: {city}"*10)
                        if len(city.split(" ")) > 1: city_lnk = "-".join(city.lower().split(" "))
                        else: city_lnk = city.lower()
                        os.chdir(f"{city}")
                        # location: ... attsearch/csv_files/{state}/{city}
                        city_ttl = 0
                        for category in t_categories:

                            cat_ttl = 0
                            
                            with open(f"{category}.csv", mode='w') as sheet:

                                writer = csv.writer(sheet, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                                writer.writerow(["Firm", "Address", "Phone"])

                                print(f"Category: {category}"*10)

                                if len(category.split(" ")) > 1: category_lnk = "-".join(category.lower().split(" "))
                                else: category_lnk = category.lower()
                                pg = ""
                                lawyers_com = f"https://www.lawyers.com/all-legal-issues/{city_lnk}/{state_lnk}/law-firms{pg}/?={category_lnk}"
                                try:

                                    soup = mk_rqst(lawyers_com)

                                    #len(list(soup.find("ul", {"class": "pagination"}).find_all("li"))) > 0:
                                    try:
                                        pgs = int(soup.find("ul", {"class": "pagination"}).find_all("li")[7].text)
                                    except:
                                        pgs = 1

                                    for pg in range(pgs+1):
                                        pg = f"-p{str(pg)}"
                                        lawyers_com = f"https://www.lawyers.com/all-legal-issues/{city_lnk}/{state_lnk}/law-firms{pg}/?={category_lnk}"
                                        soup = mk_rqst(lawyers_com)
                                        for contact in soup.find_all("div", {"class": "search-results-list"}):
                                            try:
                                                firm = next(contact.find("h2", {"class": "srl-name"}).a.stripped_strings)
                                                loc = next(contact.find("p", {"class": "srl-serving"}).stripped_strings)
                                            except:
                                                print("error with link: ", lawyers_com, "\n", "Page: ", pg, "\n", "Cat: ", category)
                                                continue
                                            phone = get_phone_num(contact)
                                            writer.writerow([firm, loc, phone])
                                            print("Firm: ", firm)
                                            print("Location: ", loc)
                                            print("Phone Num: ", phone)
                                            cat_ttl += 1
                                except:
                                    continue
                            city_ttl = cat_ttl
                        city_writer.writerow([city, city_ttl])
                        stt_ttl += city_ttl
                        os.chdir("..")
                        # location: ... attsearch/csv_files/{state}
                    os.chdir("..")
                    # location: ... attsearch/csv_files/
                stt_writer.writerow([state, stt_ttl])
            except:
                continue

mkfiles(t_states, t_state_cities, default_path)