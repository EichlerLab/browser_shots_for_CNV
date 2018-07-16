# browser_shots_for_CNV
Creates a pdf booklet of tracks for visualizing array CGH / RPKM per family for large cohorts 
You'll need: 
1. A bedfile containing the coordinates of the CNV, along with the family ID as the 4th column 
2. sessions.txt file 

To create a sessions file, go to genometest2 and create one. Replace the famil ID with 'dummy'. The Snakemake looks for this and replaces it with 
the family ID in each iteration. 

!! Do not forget: You will also have to modify the filepath to your home directory in Snakemake for the pipeline to run !! 
