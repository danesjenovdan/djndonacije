# start with the nodejs image, calling it 'build'
FROM node:18-alpine as build
RUN apk add --update --no-cache python3 make g++

RUN mkdir /app
WORKDIR /app

# install node modules
COPY package.json package-lock.json ./
RUN npm install

# build assets
COPY . .
EXPOSE 3000

RUN npm run build

# change base image
FROM nginx:alpine

COPY ./nginx.conf /etc/nginx/conf.d/default.conf

# copy built files from the 'build' container into the nginx container
COPY --from=build /app/dist /usr/share/nginx/html
