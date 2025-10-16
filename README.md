# Introduction 
This project allows for the adquisition of structured data as a .json file of the contents of both types of INE ID: "G" and "E"
by using PaddleOCR to obtain the data and heuristics to order, organize and fill it. Although it is meant to be run as a service
through a REST API, Jupyter files of the project are also included to test and update without the need of additional hardware.

# Getting Started
As stated above, this project relies on PaddleOCR and it's dependencies, as such, PaddlePaddle and PaddleOCR installation might be needed.
The following libraries, dependencies and hardware are required in order to build and run this project:
1.  Docker CLI and DockerDesktop v4.47.0 or above
2.	paddlepaddle >=3.0.0 (For GPU use, paddlepaddle-gpu v3.1.0 is already annexed on the .tar file)
3.	fastapi (when running on a container)
5.  A computer with the latest NVIDIA drivers and the required CUDA toolkit version (only when using paddlepaddle-gpu, a toolkit of CUDA 12.9 is recommended)
6.  If a GPU with the sm_120 architecture (50 series) is available, the included .tar file is made for allowing the projecto to run in this architecture only

Although paddlepaddle as of the time of writing has released version 3.2.0, no tests have been made using this version, so it is not 
recommended to use on the project as it may result in unexpected behaviour.

# Build and Test
##MacOS and Non-GPU variants:
For test and running using Jupyter notebooks, it is only necessary to run the added .ipynb file. 
For test in containers using Docker, it's necessary to build it using the dockerfile "ocr_api_docker.dockerfile" with the following command:
```docker build --no-cache -t ocr_api_docker -f ocr_api_docker.dockerfile .```
As for running on local, the command used is: ```docker run -d -p 8000:8000 ocr_api_docker```
Running on a container while on a Container Instance requires the use of a different command since credentials are managed using 
a Managed Identity, removing the need to copy them manually : ```docker run -d -p 8000:8000 ocr_api_docker```
##GPU variants on Windows:
For building the container image on a local enviroment, it is necessary to build the project using the dockerfile "ocr_api_docker_gpu50.dockerfile" if a GPU using 
the sm_120 architecture (50 series) is available, if the available GPU is from an earlier architecture (40 series or below), "ocr_api_docker_gpu.dockerfile" should be used to build.
For building, use following command: ```docker build --no-cache -t ocr_api_docker -f {DOCKERFILE} .```.
As for running on local, the command needed is:  ```docker run -it --gpus all -p 8000:8000 {DOCKERFILE}```.
