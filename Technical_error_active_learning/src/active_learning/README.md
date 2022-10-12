
# Introduction

Instructions for deploying the analysis environment and descriptions of the code and workflows within.


## Set Up and Installation


1. Open command line and navigate to the unpacked directory

You can get the path by 'Copy address as text' in the URL of your file manager.
Be sure to stick the url in it's own quotes as below. This enters it as a string and will allow CMD to read any spaces in the path correctly.


```bash
cd "C://mypath/directory/my project/subfolder"
```

2. Build the docker image

```bash
docker build -t data_analysis_r_python_img .
```

3. Run your container on port 9998

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
docker run -p 8888:8888 -v "%PWD":/app --name data_analysis_r_python_ctnr data_analysis_r_python_img
```

The way it works is by:
a. starting a Docker Container
b. Mounting your current directory ("%CD%") to
a directory in the container ("/app") so that files can be shared and moved in and out.
c. starting a Jupyter server.

4. If it has started correctly, you'll get a url token. Copy the token provided into your brower URL

It should look like this:

`http://127.0.0.1:8888/?token=3c96d2a50decb4302c3e96b87ba7444d286e335d07c478fe`

It should open up a Jupyter File explorer in the directory in your browser.

## Usage

### Python Jupyter Notebooks

To run Jupyter Notebooks, copy the token provided into your brower URL

It should look like this:

`http://127.0.0.1:8888/?token=3c96d2a50decb4302c3e96b87ba7444d286e335d07c478fe`

It should open up a Jupyter File explorer in the directory in your browser.

### Executing Scripts

You need to enter the Docker Container in a terminal to do this. As the terminal window you have been using is displaying the logs for the Jupyter Server, you need to open a new terminal window. Do so and navigate back to the directory using the instructions in **1.** of **Set Up and Installation**.

Enter the docker container with the following command.

```bash
docker exec -it data_analysis_r_python_ctnr /bin/bash
```




## Generating key pair
```bash
ssh-keygen
```