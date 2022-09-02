# Automate Duty - Version 2

The script searches the DNAnexus for recently created production projects '002_' and generates download links that are saved to a .csv file. 

An email is sent to the Duty Bioinformatician with instructions on how to download the files to the appropriate locations on the GST-Trust network. 

The script supports the following projects:

* WES
* TSO500
* SNP
* MokaPipe



Clone this repository

```
git clone https://github.com/moka-guys/Automate_Duty.git
```
## Creating the docker image 

Change directory to Automate_Duty_Docker, which contains the dockerfile 

```
cd ./Automate_Duty_docker
```

Build the docker image 

```
docker build --tag automate_duty:v2.0.0 .
```

```
docker save automate_duty:v2.0.0 | gzip > automate_duty_v2.tgz
```

Once the docker image is build uplaod it to the DNAnexus 001_ToolsReferenceData
Make sure to delete previous version of docker image.

## Creating the DNAnexus App

Using dx commmands select the project and folder where the App is supposed to go

Example:
``` 
dx select  001_ToolsReferenceData
dx cd Apps
```

Change directory to Automate_Duty_App

```
cd ./Automate_Duty_App
```

```
dx build
```

The app will apear in the DNAnexus.

## Running the app

The app requires two inputs, which are:

* DNAnexus Project ID 
* Project type - choise of the following options (WES, SNP, TSO500, MokaPipe)

## Processing the CSV email 

Intructions to process the csv containing DNAnexus download links can be found in process_csv_on_TrustPC_windows folder

## Additional infomration 

If the docker image is changed remember to also change the DNAnexus project id information in the bash script Automate_Duty_App/src/code.sh

## Developers
Igor Malashchuk\
STP Trainee in Clinical Bioinformatics\
Guy's and St Thomas's NHS Trust\
Date modified: 2nd September 2022






