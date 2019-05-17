from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import os, csv, re, json, sys, psycopg2

# Input: link; Output: beautifulsoup document (lxml)
def mk_rqst(lnk):
    req = Request(lnk, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    return BeautifulSoup(webpage, 'lxml')

# Finds the number of pages that need to be scanned through
def find_pgs(state, category):
    lnk = f"https://www.lawyers.com/all-legal-issues/all-cities/{state}/law-firms/?s={category}"
    return [i for i in mk_rqst(lnk).find(class_='pagination').find_all('li')[-2].a.strings][0]

# Inserts information into database and closes connection
def add_to_db(name, address, phone, website):
    conn = psycopg2.connect("dbname={} user={} host={}".format("lawyer_db", "postgres", "localhost"))
    c = conn.cursor()

    c.execute("INSERT INTO {} (name, address, phone, website) VALUES ('{}','{}','{}','{}')".format("lawyers", name, address, phone, website))
    conn.commit()

    c.close()
    conn.close()

# Uses Google Places API to find the address of a business given it's name
# Used on addresses that are in db only as 'Serving city, state' rather than full address
def find_addr(firm_name, city):
    firm_name = firm_name.replace(' ','%20')
    info = json.load(f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={firm_name}&inputtype=textquery&fields=formatted_address&locationbias=city:{city}&key={API_KEY}")
    return info['formatted_address']

# Given a category and state, it makes a request and looks through
# the returned document for each law firm and its information.
# Once it's found, it places it into a dictionary and also
# commits it to the database
def main(category, state):
    pgs = find_pgs(state, category)
    nm_addr = {}
    for p in range(1,int(pgs)+1):
        s = mk_rqst(f"https://www.lawyers.com/all-legal-issues/all-cities/{state}/law-firms-p{str(p)}/?s={category}")
        for sect in s.find_all(class_="search-results-list"):
            name, address = [data for i,data in enumerate(sect.find(class_="srl-summary").find(class_="name-address").stripped_strings) if i<2]
            if "Serving" in address:
                a = re.match(r'Serving\W+((\w+(\W?\w+){1,2}?),(\W\w{2}))', address)
                city,state = a[2],a[4]
                address = find_addr(name, city)
            contact_info = sect.find(class_="srl-contact-info-only")
            phone = next(contact_info.find(class_="srl-phone").stripped_strings)
            if phone=="View Phone #":
                phone = contact_info.find(class_="srl-phone").a['data-phonenum']
            website = contact_info.find(class_="srl-website").a['href']
            nm_addr[name] = [address, phone, website]
            add_to_db(name=name, address=address, website=website, phone=phone)
    return nm_addr

if __name__=="__main__":
    for category in sys.argv[1]:
        main(category, "California")
