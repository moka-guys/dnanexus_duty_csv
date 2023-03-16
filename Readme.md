# Dnanexus Duty CSV

This is the DNAnexus implementation of [duty_csv](https://github.com/moka-guys/duty_csv). It is intended to run at the end of all DNAnexus workflows. For further details on what the underlying script does and produces, please refer to that repository.

## Inputs
* project_name - DNAnexus project name to generate the CSV file for
* tso_pannumbers - TSO pan numbers used by the app to define Synnovis TSO pan numbers as we only need to download those files to the GSTT network
* stg_pannumbers - Used by the app to determine which files need to be downloaded to the St George's area and which need to be downloaded to the Synnovis area
* testing (optional) - Default is false. Set as true if you are running the app in test mode as it generates testing-specific download paths

## Outputs

The app sends an email to config-specified address, and produces the following outputs:
* logfile - for audit trail
* csv - file containing DNAnexus URLs
* html - used for email message

## What is required for this app to run?

The app requires the following inputs: 
* DNAnexus project_id (to be supplied as string)
* project type (avaiable options are WES, SNP, MokaPipe, TSO500)
* amazon email server username (obtained from 001_Authentication)
* amazon email server password (obtained from 001_Authentication)
* DNAnexus read only token (obtained from 001_Authentication)

## What does this app output?

* HTML
* CSV (optional)
* Logfile

This app sends an email to mokaguys containg a csv file attachment with URL links for files required to be transfered to Dry Lab by the Duty Bioinformatician



## How does this app work?

* This app runs a python script located inside a docker image. 

## This app was made by Genome Informatics



