FROM debian:8.3
# Install packages
RUN apt-get update && apt-get install -y python3 python3-pip
# Copy app files
WORKDIR /usim
COPY . /usim
# Install dependencies
RUN pip3 install -r requirements.txt
# Run
CMD ["python3", "usim.py"]

