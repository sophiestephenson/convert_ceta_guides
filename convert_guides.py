import argparse
import csv
import os
import re
import subprocess
from pprint import pprint

import requests


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
    if os.path.exists("ceta_dashboard.csv"):
        guides = []
        with open("ceta_dashboard.csv", "r") as f:
            csvreader = csv.DictReader(f)

            for line in csvreader:
                if line["Status"] in ["Posted in CETA website", "Final draft ready"]:
                    guide_name = filenameify(line["Guide"])
                    guide_id = get_document_id_from_url(line["Draft"])
                    new_guide = {"name": guide_name, "id": guide_id}
                    guides.append(new_guide)

    else:
        print("Please download CETA dashboard")
        exit()

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


def download_doc(guide, filetype):
    name = guide["name"]
    id = guide["id"]

    format_abbv = filetype
    if filetype == "docx":
        format_abbv = "doc"

    if not os.path.exists(filetype):
        print(f"Adding required directory {filetype}/...")
        os.mkdir(filetype)


    url = f"https://docs.google.com/document/d/{id}/export?format={format_abbv}"
    file_path = os.path.join(filetype, f"{name}.{filetype}")

    if not os.path.exists(file_path):
        print(f"Downloading {file_path}...")
        r = requests.get(url)
        open(file_path, 'wb').write(r.content)  

        ## TO DO: check if the file downloaded right


def convert_to_md(guide_name):
    if not os.path.exists("markdown"):
        print(f"Adding required directory markdown/...")
        os.mkdir("markdown")

    docx = os.path.join("docx", f"{guide_name}.docx")
    md = os.path.join("markdown", f"{guide_name}.md")
    if not os.path.exists(md):
        print(f"Creating {md}...")
        bash_command = f"pandoc {docx} -o {md}"
        subprocess.check_call(bash_command.split())


def tweak_html(guide_name):
    # grab html file content
    html_file = os.path.join("html", f"{guide_name}.html")
    with open(html_file, 'r') as f:
        file_content = f.read()

    # replace heading colors with our website color
    file_content = file_content.replace("#0000ff", "#9122e6")

    # write the new content
    with open(html_file, 'w') as f:
        f.write(file_content)


def convert_all_guides_to_md():
    guides = grab_guide_urls()

    for guide in guides:
        download_doc(guide, filetype="docx")
        convert_to_md(guide["name"])


def download_all_guides_html():
    guides = grab_guide_urls()

    for guide in guides:
        download_doc(guide, filetype="html")
        tweak_html(guide["name"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-md', action='store_true')
    parser.add_argument('-html', action='store_true')

    args = parser.parse_args()
    if args.md:
        convert_all_guides_to_md()
    if args.html:
        download_all_guides_html()

    if not (args.md or args.html):
        print("Please use the flags -md or -html to indicate what type of output you want.")


    