# using ubuntu LTS version
FROM ubuntu:20.04 AS builder-image

# avoid stuck build due to user prompt
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
  apt-get install -y software-properties-common && \
  add-apt-repository ppa:deadsnakes/ppa && \
  apt-get update && \
  apt-get install --no-install-recommends -y python3.12 python3.12-dev python3.12-venv python3-pip python3-wheel build-essential git && \
  apt-get install -y ffmpeg && \
	apt-get clean && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/DannyAkintunde/Youtube-dl-scraper home/server/scraper

# create and activate virtual environment
# using final folder name to avoid path issues with packages
RUN python3.12 -m venv /home/server/venv
ENV PATH="/home/server/venv/bin:$PATH"

# install requirements
COPY requirements.txt .
RUN pip3 install --no-cache-dir wheel
RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install --no-cache-dir -r home/server/scraper/requirements.txt
RUN pip3 install --no-cache-dir playwright
RUN chmod +x home/server/scraper/install.sh
RUN .home/server/scraper/install.sh

FROM ubuntu:20.04 AS runner-image

RUN apt-get update && \
  apt-get install -y software-properties-common && \
  add-apt-repository ppa:deadsnakes/ppa && \
  apt-get update && \
  apt-get install --no-install-recommends -y python3.12 python3-venv python3-pip && \
	apt-get clean && rm -rf /var/lib/apt/lists/*

# Set python3.12 as the default python3
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1

RUN useradd --create-home server

# Change ownership of the home directory to server user
RUN chown -R server:server /home/server

USER server
RUN mkdir /home/server/code
WORKDIR /home/server/code
COPY --chown=server:server . .
COPY --from=builder-image /home/server/venv ./venv
COPY --from=builder-image /home/server/scraper ./scraper
COPY --from=builder-image /root/.cache/ms-playwright ./.cache/ms-playwright

# activate virtual environment
ENV VIRTUAL_ENV=/home/server/venv
ENV PATH="/home/server/venv/bin:$PATH"

USER server

EXPOSE 8000

# make sure all messages always reach console
ENV PYTHONUNBUFFERED=1

CMD ["hypercorn", "-b" , ":8000", "-w", "4", "main:app"]