
# Dockerfile 04/2021
# Python environment for exporting data analysis for processing on remote systems.

# Ubuntu version 20.04
FROM ubuntu:20.04

# Overwrites the R installation questions 
ENV DEBIAN_FRONTEND noninteractive

# Specifies R version
ENV R_BASE_VERSION=4.0.0

MAINTAINER Alex Perkins <a.j.p.perkins@sms.ed.ac.uk>

# Updates Ubuntu
RUN apt-get update && apt-get -y update && apt update
# Installs tools to get the cran repository
RUN apt install -y software-properties-common && apt update

# Installs R
RUN apt-get install -y gnupg2

# This key specifies R version 4.2.
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys E298A3A825C0D65DFD57CBB651716619E084DAB9
RUN add-apt-repository 'deb https://cloud.r-project.org/bin/linux/ubuntu focal-cran40/'
RUN apt update
# Installs R 
RUN apt-get install -y --no-install-recommends build-essential r-base

# Installs Python
RUN apt-get install -y build-essential python3.6 python3-pip python3-dev

# Upgrades the Python Package Manager
RUN pip3 -q install pip --upgrade

# Makes a directory in the Ubuntu Root called /app
# Sets it to the directory to work in
# Copies everything over from the current local directory into /app
RUN mkdir app
WORKDIR app/
COPY . .

# Installs the Python packages
RUN pip3 install -r installation/python_requirements.txt

# installs Jupyter
RUN pip3 install jupyter

# Runs the R script that handles the R Libraries installation
RUN Rscript installation/install_dependencies.r

WORKDIR /app/

# Runs Jupyter Notebook on startup
CMD ["jupyter", "notebook", "--port=8888", "--no-browser", "--ip=0.0.0.0", "--allow-root"]
