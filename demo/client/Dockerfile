FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y ftp expect net-tools

COPY ftp_random_actions.exp /usr/local/bin/

COPY ./dumbfiles/ ./

RUN chmod +x /usr/local/bin/ftp_random_actions.exp

ENTRYPOINT ["/usr/local/bin/ftp_random_actions.exp"]
