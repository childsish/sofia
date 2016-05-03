#!/usr/bin/env bash

echo "Making directories"

for dirname in data data/genomic_feature data/chromosome_sequence data/sequence_variant data/txt
do
    if [ ! -e ../$dirname ]
    then
        mkdir ../$dirname
    fi
done

echo "Downloading and indexing GRCh37 sequence"
wget ftp://ftp.sanger.ac.uk/pub/gencode/Gencode_human/release_19/GRCh37.p13.genome.fa.gz -O ../data/chromosome_sequence/GRCh37.fasta.gz
gunzip ../data/chromosome_sequence/GRCh37.fasta.gz
bgzip ../data/chromosome_sequence/GRCh37.fasta
samtools faidx ../data/chromosome_sequence/GRCh37.fasta.gz

echo "Downloading and indexing GRCh37 genomic features"
wget ftp://ftp.sanger.ac.uk/pub/gencode/Gencode_human/release_19/gencode.v19.annotation.gtf.gz -O ../data/genomic_feature/GRCh37.gtf.gz
(zgrep ^"#" ../data/genomic_feature/GRCh37.gtf; zgrep -v ^"#" ../data/genomic_feature/GRCh37.gtf | sort -k1,1 -k4,4n) | bgzip > ../data/genomic_feature/GRCh37.sorted.gtf.gz;
tabix -p gff ../data/genomic_feature/GRCh37.sorted.gtf.gz

echo "Downloading and indexing RefSeq genomic features"
wget ftp://ftp.ncbi.nlm.nih.gov/refseq/H_sapiens/H_sapiens/ARCHIVE/BUILD.37.3/GFF/ref_GRCh37.p5_top_level.gff3.gz -O ../data/genomic_feature/refseq.gff.gz
(zgrep ^"#" ../data/genomic_feature/refseq.gff; zgrep -v ^"#" ../data/genomic_feature/refseq.gff | sort -k1,1 -k4,4n) | bgzip > ../data/genomic_feature/refseq.sorted.gff.gz;
tabix -p gff ../data/genomic_feature/refseq.sorted.gff.gz

echo "Downloading 1000 genomes and index"
wget http://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/ALL.wgs.phase3_shapeit2_mvncall_integrated_v5b.20130502.sites.vcf.gz -O ../data/sequence_variant/1000genomes.vcf.gz
wget http://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/ALL.wgs.phase3_shapeit2_mvncall_integrated_v5b.20130502.sites.vcf.gz.tbi -O ../data/sequence_variant/1000genomes.vcf.gz.tbi

echo "Downloading Reactome"
wget http://www.reactome.org/download/current/Ensembl2Reactome.txt -O ../data/txt/reactome.txt

