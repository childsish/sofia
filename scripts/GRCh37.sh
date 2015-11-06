#!/usr/bin/env bash

echo "Making directories"

for dirname in data data/genomic_feature data/chromosome_sequence data/sequence_variant data/txt
do
    if [ ! -e ../$dirname ]
    then
        mkdir ../$dirname
    fi
done

echo "Downloading data"

# GRCh37
wget ftp://ftp.sanger.ac.uk/pub/gencode/Gencode_human/release_19/gencode.v19.annotation.gtf.gz -O ../data/genomic_feature/GRCh37.gtf.gz
wget ftp://ftp.sanger.ac.uk/pub/gencode/Gencode_human/release_19/GRCh37.p13.genome.fa.gz -O ../data/chromosome_sequence/GRCh37.fasta.gz

# 1000 genomes
wget http://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/ALL.wgs.phase3_shapeit2_mvncall_integrated_v5b.20130502.sites.vcf.gz -O ../data/sequence_variant/1000genomes.vcf.gz
wget http://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/ALL.wgs.phase3_shapeit2_mvncall_integrated_v5b.20130502.sites.vcf.gz.tbi -O ../data/sequence_variant/1000genomes.vcf.gz.tbi

# Reactome
wget http://www.reactome.org/download/current/Ensembl2Reactome.txt -O ../data/txt/reactome.txt

echo "Sorting, compressing and indexing data"

# GRCh37
gunzip ../data/genomic_feature/GRCh37.gtf.gz
(grep ^"#" ../data/genomic_feature/GRCh37.gtf; grep -v ^"#" ../data/genomic_feature/GRCh37.gtf | sort -k1,1 -k4,4n) | bgzip > ../data/genomic_feature/GRCh37.gtf.gz;
tabix -p gff ../data/genomic_feature/GRCh37.gtf.gz
samtools faidx ../data/chromosome_sequence/GRCh37.fasta.gz
