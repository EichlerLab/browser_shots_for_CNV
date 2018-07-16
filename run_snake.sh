 snakemake -s Snakefile --drmaa " -V -cwd -w n -e ./log -o ./log {params.sge_opts} -S /bin/bash" -j 20 -w 60 -kT  ;
