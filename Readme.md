# DNAnexus Duty CSV

This is the DNAnexus implementation of [duty_csv v2.5.0](https://github.com/moka-guys/duty_csv/releases/tag/v2.5.0). It is intended to run at the end of all DNAnexus workflows. For further details on what the underlying script does and produces, please refer to that repository.

## Inputs

The app takes the following inputs: 

* project_name - DNAnexus project name to generate the CSV file for
* tso_pannumbers - TSO pan numbers. Comma separated string. Used by the app to define Synnovis TSO pan numbers as we only need to download those files to the GSTT network
* stg_pannumbers - St George's pan numbers. Comma separated string. Used by the app to determine which files need to be downloaded to the St George's area and which need to be downloaded to the Synnovis area
* cp_capture_pannos - Synnovis Custom Panels whole capture pan numbers. Comma separated string. Used by the app to determine which files need to be downloaded to both the St George's area and the Synnovis area
* testing (optional) - Default is false. Set as true if you are running the app in test mode as it generates testing-specific download paths

## Outputs

The app sends an email to config-specified address, and produces the following outputs:
* CSV (optional) - file containing DNAnexus URLs
* HTML - used for email message
* TXT - text file containing chrome downloads commands
* Logfile - for audit trail
  
This app sends an email to mokaguys containg a csv file attachment with URL links for files required to be transfered to Dry Lab by the Duty Bioinformatician

## How does this app work?

* This app runs a python script located inside a docker image.

## Developed by the Synnovis Genome Informatics Team
