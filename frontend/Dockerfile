# start with the nodejs image, calling it 'build'
FROM node:26-alpine as build

# set current directory
WORKDIR /app

# install dependencies
COPY package.json package-lock.json ./
RUN npm ci

# build assets
COPY . .
ARG VITE_API_URL
RUN npm run build

# change base image
FROM nginx:alpine

# copy custom nginx config
COPY ./nginx.conf /etc/nginx/conf.d/default.conf

# copy built files from the 'build' container into the nginx container
COPY --from=build /app/dist /usr/share/nginx/html
