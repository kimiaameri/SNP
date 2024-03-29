import csv
import sys

if len(sys.argv) < 5:
    sys.stderr.write('No Input CSV file and miniconda path GITHUB_PATH\n')
    sys.exit(0)
    
inputFile = sys.argv[1]
minicondaBin = sys.argv[2]
githubPath = sys.argv[3]
n= sys.argv[4]
index = n.split('.')[0][10:]
outputFile ="snp{}.sh".format(index)

with open(outputFile,'w') as outFile:
    outFile.write('#!/bin/sh \n')
    outFile.write('#SBATCH --time=100:00:00   # Run time in hh:mm:ss  \n')
    outFile.write('#SBATCH --mem-per-cpu=64gb  \n')
    # Maximum memory required per CPU (in megabytes')
    outFile.write('#SBATCH --job-name=variantAnalysis \n')
    outFile.write('#SBATCH --error=variantAnalysis.%J.err \n')
    outFile.write('#SBATCH --output=variantAnalysis.%J.out \n')  
    count=0
    with open(inputFile) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        
        for row in csv_reader:
              outFile.write(f' cd $WORK/SNP/data/\n' )
              outFile.write(f" cat  filtered_{row[2]} | grep -o 'length=.*$' | cut -f2 -d'=' > $WORK/SNP-outputs/length/{row[0]}.txt  \n" )
              outFile.write(f' cd $WORK/SNP-outputs/length/\n' )
              ak = "awk '{ total += $1; count ++ } END { print total/count }'"
              outFile.write(f' {ak}  {row[0]}.txt > length_{row[0]}.txt \n' )
              outFile.write(f'export LengthReverse=$(( `cat length_{row[0]}.txt` ))  \n' )
              outFile.write("LengthReverse=${LengthReverse%.*} \n")
              outFile.write(f'{minicondaBin}trimmomatic PE -threads 4 -phred33 -trimlog $WORK/SNP-outputs/trimmomatic/trimlog/{row[0]}.trimlog $WORK/SNP/data/filtered_{row[1]} $WORK/SNP/data/filtered_{row[2]} $WORK/SNP-outputs/trimmomatic/{row[0]}-R1.paired.fq $WORK/SNP-outputs/trimmomatic/{row[0]}-R1.unpaired.fq $WORK/SNP-outputs/trimmomatic/{row[0]}-R2.paired.fq $WORK/SNP-outputs/trimmomatic/{row[0]}-R2.unpaired.fq SLIDINGWINDOW:4:15 MAXINFO:50:0.5 LEADING:3 TRAILING:3 MINLEN:$LengthReverse \n')
              outFile.write(f' cd $WORK/SNP-outputs/trimmomatic/\n' )
              outFile.write(f'sed "s/\(^[@|\+].*RR[0-9]*\.[0-9]*\)\.[0-9] \(.*\)/\\1 \\2/" {row[0]}-R1.paired.fq > refined-{row[0]}-R1.paired.fq\n')
              outFile.write(f'sed "s/\(^[@|\+].*RR[0-9]*\.[0-9]*\)\.[0-9] \(.*\)/\\1 \\2/" {row[0]}-R2.paired.fq > refined-{row[0]}-R2.paired.fq\n')
              outFile.write(f'{minicondaBin}bwa mem $WORK/SNP_reference_genome/Staphylococcus_aureus_NCTC_8325/NCBI/2006-02-13/Sequence/BWAIndex/genome.fa $WORK/SNP-outputs/trimmomatic/refined-{row[0]}-R1.paired.fq $WORK/SNP-outputs/trimmomatic/refined-{row[0]}-R2.paired.fq >$WORK/SNP-outputs/samfiles/{row[0]}.sam\n')
              outFile.write(f'{minicondaBin}/samtools view -bt $WORK/SNP_reference_genome/Staphylococcus_aureus_NCTC_8325/NCBI/2006-02-13/Sequence/BWAIndex/genome.fa $WORK/SNP-outputs/samfiles/{row[0]}.sam >$WORK/SNP-outputs/bamfiles/{row[0]}.bam\n')
              outFile.write(f'{minicondaBin}/samtools flagstat $WORK/SNP-outputs/bamfiles/{row[0]}.bam > $WORK/SNP-outputs/flagsam/{row[0]}.flagstat.log\n')
              outFile.write(f'{minicondaBin}/samtools sort $WORK/SNP-outputs/bamfiles/{row[0]}.bam -O bam -o $WORK/SNP-outputs/sortsam/{row[0]}.sorted.bam\n')
              outFile.write(f'{minicondaBin}/samtools stats $WORK/SNP-outputs/sortsam/{row[0]}.sorted.bam >$WORK/SNP-outputs/stats/{row[0]}.txt \n')
              outFile.write(f'{minicondaBin}picard MarkDuplicates I=$WORK/SNP-outputs/sortsam/{row[0]}.sorted.bam O=$WORK/SNP-outputs/picard/{row[0]}.picard.bam M=$WORK/SNP-outputs/picard/picardlog/{row[0]}.picard.log\n')
              outFile.write(f'{minicondaBin}freebayes -f $WORK/SNP_reference_genome/Staphylococcus_aureus_NCTC_8325/NCBI/2006-02-13/Sequence/WholeGenomeFasta/genome.fa $WORK/SNP-outputs/picard/{row[0]}.picard.bam >$WORK/SNP-outputs/freebayesoutput/{row[0]}.vcf\n')
              outFile.write(f'{minicondaBin}samtools depth -a $WORK/SNP-outputs/sortsam/{row[0]}.sorted.bam > $WORK/SNP-outputs/depth/{row[0]}.depth\n')
              outFile.write(f'{minicondaBin}vcf2bed < $WORK/SNP-outputs/vcffilter-q-dp/{row[0]}.vcf > $WORK/SNP-outputs/vcfbed/{row[0]}.bed \n')
              #outFile.write(f'{minicondaBin}bedtools intersect -a $WORK/SNP-outputs/vcfbed/{row[0]}.bed -b {genomeBedpath}nctc8325.bed > $WORK/SNP-outputs/intersection/{row[0]}.bed \n')
              #outFile.write(f' cd $WORK/SNP-outputs/freebayesoutput/\n' )
              #outFile.write(f" cat {row[0]}.vcf | grep -v '##'| grep -v '#'| cut -f6 -d'=' > $WORK/SNP-outputs/quality/{row[0]}.txt  \n" )
              #outFile.write(f' cd $WORK/SNP-outputs/quality/\n' )
              #ak = "awk '{ total += $1; count ++ } END { print total/count }'"
              #outFile.write(f' {ak}  {row[0]}.txt > quality_{row[0]}.txt \n' )
              # outFile.write(f'export QUAL=$(( `cat quality_{row[0]}.txt` *1 ))  \n' )
              # outFile.write("QUALITY=${QUAL%.*} \n")
              #outFile.write(f'{minicondaBin}vcffilter -f "QUAL >$QUALITY " $WORK/SNP-outputs/freebayesoutput/{row[0]}.vcf >$WORK/SNP-outputs/vcffilter-q/{row[0]}.vcf\n')
              outFile.write(f' cd $WORK/SNP-outputs/depth/\n' )
              outFile.write(f" cat {row[1]} | cut -f2 -d'=' > $WORK/SNP-outputs/depth/{row[0]}.txt  \n" )
              outFile.write(f' cd $WORK/SNP-outputs/depth/\n' )
              ak = "awk '{ total += $1; count ++ } END { print total/count }'"
              outFile.write(f' {ak}  {row[0]}.txt > depth_{row[0]}.txt \n' )
              outFile.write(f'export DEPTH=$(( `cat depth_{row[0]}.txt` *1 ))  \n' )
              outFile.write("DEPTH=${DEPTH%.*} \n")
              outFile.write(f'{minicondaBin}vcffilter -f "DP > $DEPTH " $WORK/SNP-outputs/freebayesoutput/{row[0]}.vcf > $WORK/SNP-outputs/vcffilter-dp/{row[0]}.vcf\n')
              outFile.write(f'{minicondaBin}bcftools view -Ob $WORK/SNP-outputs/vcffilter-dp/{row[0]}.vcf > $WORK/SNP-outputs/bcfoutput/{row[0]}.vcf.gz\n')
              outFile.write(f'{minicondaBin}bcftools index $WORK/SNP-outputs/bcfoutput/{row[0]}.vcf.gz\n')
    outFile.write('sed -i \'s/^chr/Chromosome/\' $WORK/SNP-outputs/vcffilter-dp/*.vcf;\n')
    count=0
    with open(inputFile) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            outFile.write("cd $WORK/SNP/ \n")
            outFile.write(f'{minicondaBin}snpEff -v -ud 0 Staphylococcus_aureus_subsp_aureus_nctc_8325 $WORK/SNP-outputs/vcffilter-q-dp/{row[0]}.vcf > $WORK/SNP-outputs/snpEff/{row[0]}.ann.vcf \n')
            outFile.write(f'mv $WORK/SNP/snpEff_genes.txt $WORK/SNP-outputs/snpEff/snpEff-gene/{row[0]}.txt \n')
            outFile.write(f'mv $WORK/SNP/snpEff_summary.html $WORK/SNP-outputs/snpEff/snpEff-summary/{row[0]}.html \n')
            outFile.write("cd $WORK/SNP-outputs/snpEff/ \n")
            filter_variant = "(TYPE[*] has 'snp')"
            outFile.write(f'cat $WORK/SNP-outputs/snpEff/{row[0]}.ann.vcf | {minicondaBin}SnpSift filter  "{filter_variant}"  > $WORK/SNP-outputs/snpEff/filtered/{row[0]}.filtered.vcf \n')
            outFile.write(f'cat $WORK/SNP-outputs/snpEff/{row[0]}.ann.vcf | {minicondaBin}SnpSift filter  " ( QUAL > 500) "  > $WORK/SNP-outputs/snpEff/filtered/quality-{row[0]}.filtered.vcf \n')

