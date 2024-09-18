FROM ubuntu:20.04 AS builder
 
ARG DEBIAN_FRONTEND=noninteractive
 
WORKDIR /app

RUN apt-get update && apt-get install -y python3
RUN python3 -m venv venv
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt .
RUN pip install -r requirements.txt
 
# Stage 2
FROM ubuntu:20.04 AS runner

RUN apt-get -y update && apt-get -y upgrade && apt-get install -y ffmpeg
RUN apt-get update && apt-get install -y python3

WORKDIR /app
 
COPY --from=builder /app/venv venv
COPY . .

ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV QUART_APP=app/main.py
 
EXPOSE 5000
 
CMD ["hypercorn", "--bind" , ":5000", "--workers", "4", "main:app"]