import csv
import os
from pprint import pprint

import requests


def setup():
    required_dirs = ["docx", "markdown"]

    for dir in required_dirs:
        if not os.path.exists(dir):
            print("Adding required directory {}...".format(dir))
            os.mkdir(dir)


def filenameify(name):
    # get rid of problematic characters
    name = name.replace(" ", "_").replace("(", "").replace(")", "")
    name = name.lower()
    return name


def get_document_id_from_url(url):
    pieces = url.split("/")
    
    for i in range(len(pieces)):
        # some have /d/<id>
        if pieces[i] == "d":
            return pieces[i+1]

        # some have open?id=<id> or edit?id=<id>
        id_loc = pieces[i].find("id=")
        if id_loc > -1:
            id = pieces[i][id_loc+3:].strip()
            return id

            
def grab_guide_urls():
    # go through ceta dashboard and get the in progress guides
    assert os.path.exists("ceta_dashboard.csv")

    guides = []

    with open("ceta_dashboard.csv", "r") as f:
        csvreader = csv.DictReader(f)

        for line in csvreader:
            if line["Status"] in ["Posted in CETA website", "Final draft ready"]:
                guide_name = filenameify(line["Guide"])
                guide_id = get_document_id_from_url(line["Draft"])
                new_guide = {"name": guide_name, "id": guide_id}
                guides.append(new_guide)

    # get a few other guides which I know exist but are new, so aren't in that CSV
    other_guides = [
        {"name": filenameify("iCloud-General Safety"),
        "id": "1udx0BF3KIZpu3ykUznxBbszgVF1wgY9AhRVt4rF9YcE"},

        {"name": filenameify("Understanding Your iCloud Data"),
        "id": "1h74MsgMs98vyGmolIHGXslLXN-xkjuDKT0-dP-3t5qk"},

        {"name": filenameify("Gmail + Google Safety"),
        "id": "1tCzbE0cpyu0yzTWKvi-sl39Eu2DOnTgKBy0BuyB_zC0"},

        {"name": filenameify("Android Safety Guide"),
        "id": "1nFfu2S_EJD4x30-cPdjaZlcErsXgHmGc83lhUvZ90V4"}
    ]

    guides += other_guides

    return guides


def download_doc(guide):
    url = "https://docs.google.com/document/d/{}/export?format=doc".format(guide["id"])
    file_path = os.path.join("docx", "{}.docx".format(guide["name"]))

    if not os.path.exists(file_path):
        print("Downloading {}...".format(file_path))
        r = requests.get(url)
        open(file_path, 'wb').write(r.content)  

        ## TO DO: check if the file downloaded right


def convert_to_md(guide):
    docx = os.path.join("docx", "{}.docx".format(guide["name"]))
    assert os.path.exists(docx)

    md = os.path.join("markdown", "{}.md".format(guide["name"]))
    if not os.path.exists(md):
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


    