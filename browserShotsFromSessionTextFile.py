import argparse
import requests
from bs4 import BeautifulSoup
import re
import sys
import os

def get_browsershot(server_url, session_file, position_string, ofname, rexp, continue_on_error):
    if "genometest.gs.washington.edu" in server_url:
        hgsid = "?hgsid=100000"
    else: 
        hgsid = ""
    url = "".join([server_url, "/cgi-bin/hgTracks", hgsid, "?hgS_doLoadUrl=submit&hgS_loadUrlName=", session_file, "&hgt.psOutput=on&pix=1000", position_string])
    page = requests.get(url)
    if page.status_code != requests.codes.ok:
        print("Invalid page URL: %s" % url)
        print("Make sure your session file is globally readable and in a web-accessible directory")
        if not continue_on_error:
            sys.exit(1)
        else:
            return

    soup = BeautifulSoup(page.text, "html.parser")
    relative_url = None
    for entry in soup.find_all(href=re.compile("pdf")):
        if entry.parent.find(text=rexp) is not None:
            relative_url = entry.get("href")
            break

    if relative_url is None:
        print("Could not find browsershot pdf at %s" % url)
        print("Make sure your session file is globally readable and in a web-accessible directory")
        if not continue_on_error:
            sys.exit(1)
        else:
            return

    pdf_url = server_url + relative_url.replace("../", "/")
    print(ofname)
    with open(ofname, "wb") as outfile:
        r = requests.get(pdf_url)
        if r.status_code == requests.codes.ok:
            outfile.write(r.content)
        else:
            print(r.headers)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--regions_file", type = argparse.FileType("r"), help="Gets browsershots for multiple regions. Must be a path to tab-delimited file with list of region, outfile name, and session name (chr,start,end,ofname,sessionname).")
    group.add_argument("--region", default = None, nargs=5, metavar=("chr", "start", "end", "outfile", "session_file"), help="Get browsershot for single region.")
    parser.add_argument("--server_url", default="https://<username>:<password>@genometest2.gs.washington.edu", help="Server URL (May require username and password)")
    parser.add_argument("--continue_on_error", action='store_true')
    parser.add_argument("--pad", type=int, default=0, help="Pad start and end by pad bp")

    args = parser.parse_args()

    server_url = args.server_url
    if "<username>" in server_url:
        if "BROWSER_USERNAME" not in os.environ:
            print("Error: BROWSER_USERNAME variable not set")
            sys.exit(1)
        server_url = server_url.replace("<username>", os.environ["BROWSER_USERNAME"])
    if "<password>" in server_url:
        if "BROWSER_PASSWORD" not in os.environ:
            print("Error: BROWSER_PASSWORD variable not set")
            sys.exit(1)
        server_url = server_url.replace("<password>", os.environ["BROWSER_PASSWORD"])


    rexp = re.compile("the current browser graphic in PDF")

    regions = []
    if args.regions_file is not None:
        for line in args.regions_file:
            regions.append(line.rstrip().split())
    else:
        regions.append(args.region)

    for region in regions:
        position_string = "&position={}:{}-{}".format(region[0], int(region[1]) - args.pad, int(region[2]) + args.pad)
        outfile = region[3]
        session_file = os.path.abspath(region[4])
        get_browsershot(server_url, session_file, position_string, outfile, rexp, continue_on_error = args.continue_on_error)
