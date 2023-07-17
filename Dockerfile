FROM python:3.9.16-slim

# RUN apt-get -qq update && \
#     apt-get -qq install -y --no-install-recommends wget bzip2 libopenblas-dev pbzip2 libgl1-mesa-glx libglib2.0-0 build-essential && \
#     apt-get -qq clean && \ 
#     rm -rf /var/lib/apt/lists/*

COPY ["requirements.txt", "*.py" , "/opt/spyke/"]
WORKDIR /opt/spyke/
RUN pip install --no-cache-dir -r requirements.txt
