FROM python:3-alpine3.15
WORKDIR /app
COPY . /app
RUN bash install.sh
RUN python -m pip install -r requirements.txt
EXPOSE 5000
CMD ["hypercorn", "main:app"]
