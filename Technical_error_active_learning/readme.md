# **Jobs:**

* ~Write Parser to convert the design_real.csv into a nested json containing the new pipetting settings to be iterated over for each experiment/replicate. The doe script takes replicated into account in the design so this should be straightforward.~
* Convert pipetting script to iterate over the pipetting settings nested json.
  * **Note:** now the _experiment_settings are sorted =  use those to look them up in pipetting_settings_dict
* Build doe script for screening parameters.
* Write scripts to analyse experimental design.
* ~Randomise replicates across plate.~
* Test multiple lysates


# **Introduction**

Instructions for deploying the analysis environment and descriptions of the code and workflows within.


# **The Dockerised Analysis Python and R Environment**

## **Setup and Installation**


### **1. Open command line and navigate to the unpacked directory**

You can get the path by 'Copy address as text' in the URL of your file manager.
Be sure to stick the url in it's own quotes as below. This enters it as a string and will allow CMD to read any spaces in the path correctly.


```bash
cd "C://mypath/directory/my project/subfolder"
```

### **2. Build the docker image**

```bash
docker build -t data_analysis_r_python_img .
```

**3. Run your container on port 8888**

Windows CMD:
```bash
docker run -p 8888:8888 -v "%CD%":/app --name data_analysis_r_python_ctnr data_analysis_r_python_img
```
Windows PowerShell:
```bash
docker run -p 8888:8888 -v ${pwd}:/app --name data_analysis_r_python_ctnr data_analysis_r_python_img
```

If you're on Mac or Linux:

```bash
docker run -p 8888:8888 -v $pwd:/app --name data_analysis_r_python_ctnr data_analysis_r_python_img
```

The way it works is by:
a. starting a Docker Container
b. Mounting your current directory ("%CD%") to
a directory in the container ("/app") so that files can be shared and moved in and out.
c. starting a Jupyter server.

**Note:** If it has started correctly, you'll get a url token. Copy the token provided into your brower URL

It should look like this:

`http://127.0.0.1:8888/?token=3c96d2a50decb4302c3e96b87ba7444d286e335d07c478fe`

It should open up a Jupyter File explorer in the directory in your browser.

## Usage

### **Python Jupyter Notebooks**

To run Jupyter Notebooks, copy the token provided into your brower URL

It should look like this:

`http://127.0.0.1:8888/?token=3c96d2a50decb4302c3e96b87ba7444d286e335d07c478fe`

It should open up a Jupyter File explorer in the directory in your browser.

### **Executing Scripts**

You need to enter the Docker Container in a terminal to do this. As the terminal window you have been using is displaying the logs for the Jupyter Server, you need to open a new terminal window. Do so and navigate back to the directory using the instructions in **1.** of **Set Up and Installation**.

**Enter the docker container with the following command.**

```bash
docker exec -it data_analysis_r_python_ctnr /bin/bash
```
**Execute Python scripts (.py) with:**

```bash
python3 myscript.py
```

**Execute R scripts (.) with:**

```bash
R < myscript.r --no-save
```

# **Design of Experiments**


The DoE workflow in */src* consists of the following components:

* ***components.json*** : Contains the parameters to be modulated and with min and max values.
* ***doe.r*** : The R script that takes in the parameters to be modulated in the experiment.
  * Builds a central composite design (CCD) using the number of parameters to be modulated.
  * Converts to real values using a linear regression model trained us the min and max values provided for each parameter.
  * Checks for any negative values and removes those runs.
  * Exports the design as a .csv
* ***design_real.csv*** : The output of the experimental design with the real values of the parameters encoded.
* ***design_coded.csv*** : The output of the experimental design in coded values.
* ***base_pipetting_settings.json*** : The naïve pipetting settings.
* ***experiment_design_to_json_parser.py*** : Python script that:
  * Takes the *design_real.csv*
  * Counts the number of runs and works out how any plates to spread them over.
  * Assigns plates and Wells to each.
  * Uses the *base_pipetting_settings.json* as a template and updates the values for each variable in each one as appropriate.
  * Exports a *plate_#_pipetting_settings.json* which contains the nested settings for each run under the assigned well name as a key.

## **Workflow**

1. Set Up the environment using the instructions above.  
   **Note:** *In the Docker Container, be sure to navigate into /src to find the files*
2. Change ***components.json*** for the parameters you want to modulate and provide min and max values.
3. Update the parameters inside ***doe.r*** to change the experimental design.
4. Execute ***doe.r*** using the instructions above in **Executing Scripts**.
5. Execute ***experiment_design_to_json_parser.py*** to generate the *_pipetting_settings.json* to feed to the OT2 for each experiment.






# Connecting to OT2 through ssh

## Generating key pair
```bash
ssh-keygen
```

## Sending public key to raspberry pi

### Command template - This needs to be ran in Powershell
@{key = Get-Content [ssh key file path] | Out-String} | ConvertTo-Json | Invoke-WebRequest -Method Post -ContentType 'application/json' -Uri [OT2 ip]:31950/server/ssh_keys -UseBasicParsing

```bash
@{key = Get-Content C:\users\s1530400\.ssh\id_rsa | Out-String} | ConvertTo-Json | Invoke-WebRequest -Method Post -ContentType 'application/json' -Uri 169.254.156.218:31950/server/ssh_keys -UseBasicParsing
```

## Transferring a file over

### Note!!!
Can't transfer files from M:\ datastore folder path for some reason. Transfer files from C:\.

### Command template
scp -i [ssh key file path] [file_path_from_local] root@[OT2 IP (may change - find in OT2 UI)]:[file_path_on_ot2]

```bash
scp -i C:\users\s1530400\.ssh\id_rsa C:\users\s1530400\NLLAB_OT2_Protocol_Dev\Technical_error_active_learning\src\OT2_scripts\OT2_settings\test.json root@169.254.156.218:/data/user_storage/al_cell_free
```

## Transferring a folder over

### Command template
scp -r -i [ssh key file path] [file_path_from_local] root@[OT2 IP (may change - find in OT2 UI)]:[file_path_on_ot2]

### This example transfers a whole folder called ALTE007 which contains the protocol .py file, the experiment settings json file,
### the labware settings json file and the pipetting settings json files
```bash
scp -r -i C:\users\nllab_ot2\.ssh\ot2_ssh_key C:\users\nllab_ot2\NLLAB_OT2_Protocol_Dev\Technical_error_active_learning\src\OT2_scripts\ALTE007\ root@169.254.156.218:/data/user_storage/
```

## Connecting to the OT2 raspberry pi
ssh -i ot2_ssh_key root@[OT2 IP]

```bash
ssh -i C:\Users\nllab_ot2\.ssh\ot2_ssh_key root@169.254.156.218
```

## Running the protocol from the command line (on raspberry pi)
```bash
opentrons_execute ALTE007_technical_error_AL_pipetting_script.py
```

# Experiment Diary

### ALTE001

10x replicates
First run of pipetting a lysate reaction.
Used Michael's reagents
Only one replicate worked.
Manually added the wax

### ALTE002

Repeat of ALTE001 but with automated waxing.
On the same plate as ATLE003.

### ALTE003

Same as ALTE002 but using Alex's lysate and ES as a positive control.
Will segregate the raw data files manually.


## Combined run

The pipetting script was improved to make it more dynamic and allow multiple experiments on one plate.

** Wax new tip should not be Never to avaoid cross contamination **

### ALTE006

As we had a load of trouble with ALTE005, having had to do multiple runs and seeing no signal -  To rule out MS lysate and substrates being a bit crap, we're doing a complete re-run but with AP lysate and substrates.

### ALTE007

We're also trialling sticking the substrates in first before the viscous lysate and seeing if that makes a difference. -  Used MS substrates

* ~Saw one of the end of the substrates not pick enough up. Maybe the asp_increment isn't keeping up towards the end. Decrease by 0.1 for ALTE008~

* ~turn off temp module at spin down wax pause.~

* ~Change wax step to always get new tip~

### ALTE008

Whether lysate or substrates first was a bit inconclusive due to a couple of wells missing a bit of substrates and there not being much difference besides. Hence we've decided to stick with substrates first for now.

* the script has been converted to standard for loop through the experiments - all substrates for all experiments and then all lysates.

* have lowered the substrates asp increment by 0.1 to 0.7.

This experiment will be a total repeat of the same settings.

### Notes

* Looks like all wells got consistent lysate and substrates
* Still haven't resolved the wax double dipping problem
