# Introduction

This project extracts structured data from both types of Mexican INE identification cards ("G" and "E") and outputs it as a .json file. It uses PaddleOCR to perform text recognition, combined with heuristics to organize, validate, and fill in the extracted fields.
While the project is designed to run as a REST API service, Jupyter notebooks are also included to allow testing and experimentation without additional infrastructure.

# Getting Started

As mentioned above, this project depends on PaddleOCR and its core framework PaddlePaddle. Please ensure these libraries and other dependencies are correctly installed before building or running the project.
Requirements
1. Docker CLI and Docker Desktop v4.47.0 or higher
2. paddlepaddle >= 3.0.0
    - For GPU acceleration: paddlepaddle-gpu==3.1.0
3. fastapi (required when running the service in a container)
4. A computer with the latest NVIDIA drivers and the required CUDA toolkit version
    - CUDA 12.9 is recommended for GPU-based builds.
5. If using a GPU with the sm_120 architecture (50 series), use the included .tar image for paddlepaddle which is optimized for this architecture.

### Although paddlepaddle as of the time of writing has released version 3.2.0, no tests have been made using this version, so it is not recommended to use on the project as it may result in unexpected behavior.

# Model Requirement

To enable the INE classification process, you must train a YOLOv11-cls model with labeled images of both INE types ("G" and "E"). It is recommended to use at least 5000 images per class for optimal results. Once trained, place the resulting model file (`best.pt`) in the root directory of the project before running or building the service.

# Build and Test

## MacOS and Non-GPU builds:

For test and running using Jupyter notebooks, it is only necessary to run the provided .ipynb file. 
To run inside a container, build the image using the following command: ```docker build --no-cache -t ocr_api_docker -f ocr_api_docker.dockerfile .``` 

Then start the container: ```docker run -d -p 8000:8000 ocr_api_docker```

### Note:

On CPU-only systems, OCR and inference tasks will run significantly slower than on GPU-enabled builds.

## GPU builds on Windows:

If you are building locally with GPU support, choose the appropriate Dockerfile based on your GPU architecture:
  - For sm_120 (50 Series) GPUs: use ```ocr_api_docker_gpu50.dockerfile```
  - For older GPUs (40 series or earlier): use ```ocr_api_docker_gpu.dockerfile```

Build the container using: ```docker build --no-cache -t ocr_api_docker -f {DOCKERFILE} .```

Run the container with GPU access: ```docker run -it --gpus all -p 8000:8000 ocr_api_docker```

# Licence
This project is distributed under the GNU Affero General Public License. See the ```LICENCE``` file for more details
