FROM alpine
RUN echo 'while true;do echo -e "HTTP/1.1 200 OK\n\n$(printenv)" | nc -lk -p 80;done' > /run.sh
ENTRYPOINT ["sh", "/run.sh"]
