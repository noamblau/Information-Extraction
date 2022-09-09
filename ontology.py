import requests
import lxml.html
import rdflib
import re

wiki_prefix = "http://en.wikipedia.org"
example_prefix = "http://example.org"

# ------ Relations ------ #
PRESIDENT_OF = f"{example_prefix}/president_of"
PRIME_MINISTER_OF = f"{example_prefix}/prime_minister_of"
POPULATION_OF = f"{example_prefix}/population_of"
AREA_OF = f"{example_prefix}/area_of"
GOVERNMENT_FORM = f"{example_prefix}/government_form"
CAPITAL_OF = f"{example_prefix}/capital_of"
BORN_IN = f"{example_prefix}/born_in"
BDATE = f"{example_prefix}/bdate"
# ----------------------- #

# ------ Globals ------ #
countries = []
presidents_and_prime_ministers = []
visited_countries = set()
visited_presidents_and_prime_ministers = set()
g = rdflib.Graph()
# --------------------- #


# ------ Extract data from country ------ #
def extract_president(doc):
    res = [t for t in doc.xpath("""//table[contains(@class, 'infobox')]
                                   //tr[th/descendant::text() = 'President']
                                   //td//@title""")]
    if len(res):
        return [res[0]]
    return []


def extract_prime_minister(doc):
    res = [t for t in doc.xpath("""//body[not(contains(//h1//text(),"The Bahamas"))]
                                   //table[contains(@class, 'infobox')]
                                   //tr[descendant::text() = 'Prime Minister']
                                   //td//@title""")]
    res += [t for t in doc.xpath("""//body[contains(//h1//text(),"The Bahamas")]
                                    //table[contains(@class, 'infobox')]
                                    //tr[descendant::text() = 'Prime Minister']
                                    //td//@href""")]
    if len(res):
        return [res[0].split("/")[-1].replace("_", " ")]
    return []


def extract_population(doc):
    res = [t for t in doc.xpath("""//body[not(contains(//h1//text(),"Channel Islands"))]
                                    //table[contains(@class, 'infobox')]
                                    //tr[descendant::text() = 'Population']
                                    /following-sibling::tr[1]
                                    /td[contains(@class, 'infobox-data')]//text()""")]
    res += [t for t in doc.xpath("""//table[contains(@class, 'infobox')]
                                    //tr[descendant::text() = 'Population']
                                    /following-sibling::tr[1]
                                    /td[contains(@class, 'infobox-data')]//li//text()""")]
    res += [t for t in doc.xpath("""//body[contains(//h1//text(),"Channel Islands")]
                                    //table[contains(@class, 'infobox')]
                                    //tr[descendant::text() = 'Population']
                                    /td[contains(@class, 'infobox-data')]//text()""")]
    if res[0].__eq__("\n") or res[0].__eq__(" "):
        return [res[1].strip()]
    return [res[0].split("(")[0].strip()]


def extract_area(doc):
    res = [t for t in doc.xpath("""//body[not(contains(//h1//text(),"Channel Islands"))]
                                    //table[contains(@class, 'infobox')]
                                    //tr[descendant::text() = 'Area ' or descendant::text() = 'Area']
                                    /following-sibling::tr[1]
                                    /td[contains(@class, 'infobox-data')]//text()""")]
    res += [t for t in doc.xpath("""//body[contains(//h1//text(),"Channel Islands")]
                                    //table[contains(@class, 'infobox')]
                                    //tr[descendant::text() = 'Area']
                                    /td[contains(@class, 'infobox-data')]//text()""")]
    res = res[0].split("(")
    res = res[-1]
    if re.search("km", res):
        res = res[:-3]
    return [res + " km squared"]


def extract_form_of_government(doc):
    res = [t for t in doc.xpath("""//table[contains(@class, 'infobox')][1]
                                   //tr[descendant::text() = 'Government']
                                   //td//@title""")]
    return res


def extract_capital(doc):
    ret_vals = []
    res = [t for t in doc.xpath("""//table[contains(@class, 'infobox')]
                                   //tr[descendant::text() = 'Capital']
                                   //td//a[not(descendant::i)]//@title""")]
    if not len(res):
        return []
    for t in res:
        if t.__contains__("Maps") or t.__contains__("Geographic") or t.__contains__("Status"):
            return [ret_vals[0]]
        if not t.__contains__("De jure") and not t.__contains__("De facto") and not t.__contains__("Citation") and not t.__contains__("reliable"):
            ret_vals.append(t)
    return [ret_vals[0]]
# --------------------------------------- #


# ------ Extract data from people ------ #
def extract_birth_date(doc):
    res = [t for t in doc.xpath("""//table[contains(@class, 'infobox')]
                                   //tr[contains(th/text(), 'Born')]/td
                                   //span[contains(@class, 'bday')]//text()""")]
    if len(res):
        return [res[0]]
    return []


def extract_birth_country(doc):
    res = [t for t in doc.xpath("""//table[contains(@class, 'infobox')]
                                   //tr[contains(th/text(), 'Born')]/td
                                   //@title""")]
    res += [t for t in doc.xpath("""//table[contains(@class, 'infobox')]
                                    //tr[contains(th/text(), 'Born')]/td
                                    //text()""")]
    res = [t.replace(',', ' ').replace(')', ' ').replace('(', ' ').strip() for t in res]
    for i in range(len(res)):
        if res[i] in visited_countries:
            return [res[i]]
    return []
# -------------------------------------- #


# ------ Add data to ontology ------ #
def add_to_ontology(entity, relation, items):
    if len(items) == 0:
        return

    relation_uri = rdflib.URIRef(relation)
    entity = entity.encode('utf-8', "ignore")
    entity = entity.decode()
    subject_uri = rdflib.URIRef(f"{example_prefix}/{entity}")

    # format as a URI and add
    for item in items:
        item_uri = rdflib.URIRef(f"{example_prefix}/{item.replace(' ', '_')}")
        g.add((subject_uri, relation_uri, item_uri))
# ---------------------------------- #


# ------ build_ontology ------ #
def build_ontology_country(country, doc):
    president = extract_president(doc)
    add_to_ontology(country, PRESIDENT_OF, president)
    prime_minister = extract_prime_minister(doc)
    add_to_ontology(country, PRIME_MINISTER_OF, prime_minister)
    population = extract_population(doc)
    add_to_ontology(country, POPULATION_OF, population)
    area = extract_area(doc)
    add_to_ontology(country, AREA_OF, area)
    form_of_government = extract_form_of_government(doc)
    add_to_ontology(country, GOVERNMENT_FORM, form_of_government)
    capital = extract_capital(doc)
    add_to_ontology(country, CAPITAL_OF, capital)


def build_ontology_people(person, doc):
    bdate = extract_birth_date(doc)
    add_to_ontology(person, BDATE, bdate)
    birth_country = extract_birth_country(doc)
    add_to_ontology(person, BORN_IN, birth_country)
# ---------------------------- #


# ------ Crawl data functions ------ #
def crawl_countries():
    url = "https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)"
    r = requests.get(url)
    doc = lxml.html.fromstring(r.content)
    countries_lst = doc.xpath("""//table[contains(@class, 'wikitable')]
                       //tr/td[1][not(contains(text(), '('))]//@title[not(ancestor::sup)]""")
    countries_lst += doc.xpath("""//table[contains(@class, 'wikitable')]
                       //tr/td[1][contains(text(), '(')]/span//@title[not(ancestor::sup)]""")
    for c in countries_lst:
        if c in visited_countries:
            continue
        countries.append(c)
        visited_countries.add(c)


def crawl_data_from_countries():
    for c in countries:
        c_new = c.replace(' ', '_')
        url = f"{wiki_prefix}/wiki/{c_new}"
        r = requests.get(url)
        doc = lxml.html.fromstring(r.content)
        res = [t for t in doc.xpath("""//body[not(contains(//h1//text(),"The Bahamas"))]
                                       //table[contains(@class, 'infobox')]
                                       //tr[th/descendant::text() = 'President' or descendant::text() = 'Prime Minister']
                                       //td//a[1]//@title""")]
        res.append("Philip_%22Brave%22_Davis")
        for t in res:
            if t in visited_presidents_and_prime_ministers or t.__contains__("cite_note"):
                continue
            presidents_and_prime_ministers.append(t)
            visited_presidents_and_prime_ministers.add(t)
        build_ontology_country(c_new, doc)


def crawl_data_from_people():
    for p in presidents_and_prime_ministers:
        p_new = p.replace(' ', '_')
        url = f"{wiki_prefix}/wiki/{p_new}"
        r = requests.get(url)
        doc = lxml.html.fromstring(r.content)
        build_ontology_people(p_new, doc)
# ---------------------------------- #


# ------ main ontology builder function ------ #
def build_ontology():
    crawl_countries()
    crawl_data_from_countries()
    crawl_data_from_people()
    g.serialize("./ontology.nt", encoding="utf-8", format="nt", errors="ignore")
# -------------------------------------------- #
