#!/bin/sh
#SBATCH --time=100:00:00   # Run time in hh:mm:ss
#SBATCH --mem-per-cpu=64gb     # Maximum memory required per CPU (in megabytes)
#SBATCH --job-name=SNP
#SBATCH --error=SNP.%J.err
#SBATCH --output=SNP.%J.out

export MINICONDA_HOME="~/miniconda3/envs/snpvariant/bin/"
export GITHUB_DIR=`pwd`

#-------------------- make the directories

sh makedirectories.sh
#-------------------- Download reference genome

cd SNP_reference_genome
wget ftp://igenome:G3nom3s4u@ussd-ftp.illumina.com/Staphylococcus_aureus_NCTC_8325/NCBI/2006-02-13/Staphylococcus_aureus_NCTC_8325_NCBI_2006-02-13.tar.gz
tar -xzf Staphylococcus_aureus_NCTC_8325_NCBI_2006-02-13.tar.gz
rm Staphylococcus_aureus_NCTC_8325_NCBI_2006-02-13.tar.gz

#-------------------- make the inputfile list
Rscript fileName.R $GITHUB_DIR/SNP-data $GITHUB_DIR/InputFiles.csv

split -l 10 InputFiles.csv new  
vim list.txt
for x in new*; do cat list.txt | sed 's/new/Inputfile/'$x done


for x in `cat inputs.txt`; do 
python3 pythonVariantAnalysis.py ./$x $MINICONDA_HOME $GITHUB_DIR $x
done
sh SNPS.sh

Rscript depth.R $WORK/SNP-outputs/depth/ $WORK/SNP-outputs/freebayesoutput/ depth.txt quality.txt 
export DEPTH=$(( `cat depth.txt` * 1 ))
export QUALITY=$((`cat quality.txt` * 1 ))
python3 pythonBCF_VCF.py ./InputFiles.csv $MINICONDA_HOME $QUALITY $DEPTH
sh BCF-VCF.sh
python3 pythonSnpEff.py ./InputFiles.csv $MINICONDA_HOME 
sh snpEff.sh
cd $WORK/SNP-outputs/snpEff
for x in *.vcf; do  cat $x | grep -v '##'| sed 's/AB=.*;TYPE=/TYPE=/' > $WORK/SNP-outputs/snpEff/filtered/1/$x.csv; done
find . -name "*.csv" -size <=1k -delete
