# start with the nodejs image, calling it 'build'
FROM node:22-alpine as build

# set current directory
WORKDIR /app

# install dependencies
COPY package.json yarn.lock ./
RUN yarn

# build assets
COPY . .
RUN yarn build

# change base image
FROM nginx:alpine

# copy custom nginx config
COPY ./nginx.conf /etc/nginx/conf.d/default.conf

# copy built files from the 'build' container into the nginx container
COPY --from=build /app/dist /usr/share/nginx/html
