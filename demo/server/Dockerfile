FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y vsftpd net-tools

RUN useradd -m victim42 && echo "victim42:this_is_my_password" | chpasswd

COPY vsftpd.conf /etc/vsftpd.conf

RUN mkdir -p /var/run/vsftpd/empty

COPY ./dumbfiles/ /home/victim42
RUN chmod a-w /home/victim42

RUN mkdir /home/victim42/upload
RUN chmod a+w /home/victim42/upload

EXPOSE 20-21

CMD ["vsftpd"]
