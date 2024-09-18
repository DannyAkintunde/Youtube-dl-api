FROM ubuntu:20.04 AS builder
 
WORKDIR /app

RUN apt-get -y update && apt-get -y upgrade && apt-get install -y ffmpeg
RUN apt-get update && apt-get install -y python3
RUN python3 -m venv venv
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt .
RUN pip install -r requirements.txt
 
# Stage 2
FROM ubuntu:20.04 AS runner
 
WORKDIR /app
 
COPY --from=builder /app/venv venv
COPY . .
 
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV QUART_APP=app/main.py
 
EXPOSE 8080
 
CMD ["hypercorn", "--bind" , ":8080", "--workers", "2", "main:app"]