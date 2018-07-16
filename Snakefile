import pandas as pd
import os

configfile: "config.yaml"

ALL_REGIONS = config["regions"]
REGIONS = pd.read_table(config["regions"], header=None, names=["contig", "start", "end", "name"])
REGIONS["key"] = REGIONS.contig + "_" + REGIONS.start.astype(str) + "_" + REGIONS.end.astype(str) + "_" + REGIONS.name
#REGIONS["key"] = REGIONS.contig + " " + REGIONS.start.astype(str) + " " + REGIONS.end.astype(str) + " " + REGIONS.name
REGIONS.index = REGIONS.key

passwords = os.path.expanduser(config["passwords"])

def get_regions_from_bed(bedfile, column):
    regions = []
    with open(bedfile, "r") as infile:
        for line in infile:
            regions.append(line.rstrip().split()[column])
    return regions

if not os.path.exists("log"):
    os.makedirs("log")

localrules: all

rule all:
    input: "merged/browsershots_combined.pdf"
    params: sge_opts = "-N run_all"

rule combine_browsershots:
    input: expand("browsershots/{chr}_{start}_{end}_{name}.pdf", zip, chr = get_regions_from_bed(ALL_REGIONS, 0), start = get_regions_from_bed(ALL_REGIONS, 1), end = get_regions_from_bed(ALL_REGIONS, 2), name = get_regions_from_bed(ALL_REGIONS, 3))
    output: "merged/browsershots_combined.pdf"
    params: sge_opts="-N combine_browsershots"
    shell: "gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -sOutputFile={output} {input}"

rule make_browsershots:
    input:session=config["session"],env_cfg=passwords
    params: sge_opts = "-N browsershot -l mfree=8G -l gpfsstate=0 ", full_name = "{chr}_{start}_{end}_{name}", pad=config["pad"]
    output: "browsershots/{chr}_{start}_{end}_{name}.pdf"
    run:

        elements = params.full_name.split("_")
        #pad = "10000" if int(int(elements[2])-int(elements[1])) <= 5000 else  "100000"
        pad=100000
        region = REGIONS.loc[params.full_name]
        shell ("sed 's/dummy/{elements[3]}/g'  session_dummy.txt > /net/eichler/vol6/home/smurali/public_html/tracks/{elements[2]}_{elements[3]}_paternal_settings.txt ;  ")
        shell(". {input.env_cfg}; python browserShotsFromSessionTextFile.py --region {elements[0]} {elements[1]} {elements[2]} browsershots/{params.full_name}.pdf /net/eichler/vol6/home/smurali/public_html/tracks/{elements[2]}_{elements[3]}_paternal_settings.txt  --pad {pad}")




