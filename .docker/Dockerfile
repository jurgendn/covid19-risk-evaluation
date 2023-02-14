FROM gr000a1/torch-cpu:0.4.0


RUN apt-get update
RUN pip3 install pip --upgrade
COPY requirements.txt .
RUN pip install -r requirements.txt

RUN useradd -m working
USER working
WORKDIR /home/working
COPY . .

# CMD ["python", "main.py"]
