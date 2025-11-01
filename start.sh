docker build -t gpurunner .
docker run --rm -it -d --gpus all --name gpurunner gpurunner:latest --entrypoint /bin/bash

