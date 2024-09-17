FROM python:3-alpine3.15
RUN apt-get update && \
apt-get install -y \
git
RUN git clone https://github.com/DannyAkintunde/YouTube-DL-api /root/app
WORKDIR /root/app/
COPY install.sh .
COPY requirements.txt .
RUN chmod +x /install.sh
COPY . .
EXPOSE 5000
CMD ["hypercorn", "main:app"]
