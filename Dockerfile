FROM python:3.11
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY . .

RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# Para Selenium no Docker, rodar o RUN abaixo para instalar o chrome

# RUN apt-get update && apt-get install -y wget unzip && \
#    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
#    apt install -y ./google-chrome-stable_current_amd64.deb && \
#    rm google-chrome-stable_current_amd64.deb && \
#    apt-get clean

CMD ["python", "main.py"]