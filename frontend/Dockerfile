FROM node:lts AS build
WORKDIR /usr/src
COPY yarn.lock package.json ./
RUN yarn install
COPY ./ ./
RUN yarn build

FROM nginx:1 AS server
COPY ./docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /usr/src/dist/ /usr/share/nginx/html/
