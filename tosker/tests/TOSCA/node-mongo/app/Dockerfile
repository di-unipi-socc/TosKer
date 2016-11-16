FROM ubuntu:latest
COPY package.json .
COPY main.js .

RUN apt-get update
RUN apt-get install nodejs npm -y
RUN apt-get clean
RUN ln -s /usr/bin/nodejs /usr/bin/node

RUN npm install

ENV PORT 80

CMD ["node", "main.js"]
