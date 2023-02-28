# Automate Duty

## What does this app do?

## What are typical use cases for this app?

The Automate_Duty_Docker app is designed to run at the end of DNAnexus NGS analysis wworkflows. It uses a python script to search for files required for Dry Lab transfer. It creates URL links for these files and adds saves then to a csv file which is emailed as an attachment to MokaGuys. 

## Current supported projects

The URL links are jenerated for the following files in the folloing projects:

### WES 
* \[sample...\].chanjo_txt in coverage folder 

### SNP
* \[sample...\].sites_present_reheader_filtered_normalised.vcf in output folder

### MokaPipe
* \[sample...\].exon_level.txt in coverage folder 
* combined_bed_summary... for RPKM in conifer_output folder
* \[sample...\].txt for FH_PRS in PRS_output

### TSO500
* \[sample...\].gene_level.txt in coverage folder 
* \[sample...\].exon_level.txt in coverage folder 
* Results.zip in "/" folder
* \[...\]_MergedSmallVariants.genome.vcf.stats.csv in QC folder

## What is required for this app to run?

The app requires the following inputs: 
* DNAnexus project_id (to be supplied as string)
* project type (avaiable options are WES, SNP, MokaPipe, TSO500)
* amazon email server username (obtained from 001_Authentication)
* amazon email server password (obtained from 001_Authentication)
* DNAnexus read only token (obtained from 001_Authentication)

## What does this app output?

* This app sends an email to mokaguys containg a csv file attachment with URL links for files required to be transfered to Dry Lab by the Duty Bioinformatician

## How does this app work?

* This app runs a python script located inside a docker image. 

## This app was made by Genome Informatics



