FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

WORKDIR /app

RUN apt-get update && apt-get install -y vim nvtop && rm -rf /var/lib/apt/lists/

# Copy the GPU utility script
COPY gpurunner.py /app/

# Set the entrypoint to run the GPU utility script
ENTRYPOINT ["python", "gpurunner.py"]

