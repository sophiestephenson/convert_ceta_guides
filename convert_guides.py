import csv
import os
from pprint import pprint

import requests


def setup():
    required_dirs = ["docx, markdown"]

    for dir in required_dirs:
        if not os.path.exists(dir):
            os.mkdir(dir)


def get_document_id_from_url(url):
    pieces = url.split("/")
    
    for i in range(len(pieces)):
        # some have /d/<id>
        if pieces[i] == "d":
            return pieces[i+1]

        # some have open?id=<id> or edit?id=<id>
        id_loc = pieces[i].find("id=")
        if id_loc > -1:
            return pieces[i][id_loc+3:]

            
def grab_guide_urls():
    # go through ceta dashboard (last accessed december 12, 2022) and get the in progress guides
    assert os.path.exists("ceta_dashboard.csv")

    guides = []

    with open("ceta_dashboard.csv", "r") as f:
        csvreader = csv.DictReader(f)

        for line in csvreader:
            if line["Status"] in ["Posted in CETA website", "Final draft ready"]:
                guide_name = line["Guide"].replace(" ", "_").lower()
                guide_id = get_document_id_from_url(line["Draft"])
                new_guide = {"name": guide_name, "id": guide_id}
                guides.append(new_guide)

    return guides


def download_doc(guide):
    url = "https://docs.google.com/document/d/{}/export?format=doc".format(guide["id"])
    file_path = "docx/{}.docx".format(guide["name"])

    print("Downloading {}...".format(file_path))
    r = requests.get(url)
    open(file_path, 'wb').write(r.content)  


def convert_to_md(guide):
    docx = "docx/{}.docx".format(guide["name"])
    assert os.path.exists(docx)

    md = "markdown/{}.md".format(guide["name"])
    print("Creating {}...".format(md))

    bashCommand = "pandoc {} -o {}".format(docx, md)
    os.system(bashCommand)


def convert_all_guides():
    setup()

    guides = grab_guide_urls()

    for guide in guides:
        download_doc(guide)
        convert_to_md(guide)

if __name__ == "__main__":

    convert_all_guides()


    