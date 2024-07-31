FROM node:lts AS build
WORKDIR /usr/src
COPY yarn.lock package.json ./
RUN yarn install
COPY ./ ./
RUN yarn build

FROM nginx:1 AS server
RUN echo 'absolute_redirect off;' >/etc/nginx/conf.d/relative-redirects.conf
COPY --from=build /usr/src/dist/ /usr/share/nginx/html/
