#!/bin/bash

# if image exists:

if [[ "$(docker images -q data_analysis_r_python_img 2> /dev/null)" == "" ]]; then
  
  # Check if container exists:
    if [ $( docker ps -a | grep data_analysis_r_python_ctnr | wc -l ) -gt 0 ]; then
        
        sudo docker rm data_analysis_r_python_ctnr

        sudo docker run -v $(pwd):/app --name data_analysis_r_python_ctnr data_analysis_r_python_img

    
    # if not run..
    else
        sudo docker run -v $(pwd):/app --name data_analysis_r_python_ctnr data_analysis_r_python_img
    fi

# if image doesn't exist: build then run.
else
    sudo docker build -t data_analysis_r_python_img .

    sudo docker rm data_analysis_r_python_ctnr
    sudo docker run -v $(pwd):/app --name data_analysis_r_python_ctnr data_analysis_r_python_img

fi



