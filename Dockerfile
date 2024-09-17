FROM python:3-alpine3.15
RUN git clone https://github.com/DannyAkintunde/YouTube-DL-api /root/app
WORKDIR /root/app/
COPY install.sh .
RUN chmod +x /install.sh
RUN python -m pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["hypercorn", "main:app"]
