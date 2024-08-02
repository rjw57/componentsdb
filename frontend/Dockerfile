# syntax=docker/dockerfile:1.7-labs
FROM node:lts AS dependencies
WORKDIR /usr/src/app
COPY yarn.lock package.json ./
RUN yarn install
ENTRYPOINT ["yarn"]

FROM dependencies AS dev
HEALTHCHECK \
  --interval=30s \
  --retries=5 \
  --start-period=120s \
  --start-interval=1s \
  CMD ["curl", "--fail", "http://localhost:3000/healthy"]
# The JS ecosystem in general likes to keep node_modules in the root which is a bit of a pain when
# we bind-mount into the container. As such the non-src/ directories are baked into the container
# and we need to manually mount any special files/directories as necessary.
COPY --exclude=src/ ./ ./
CMD ["start", "--host", "0.0.0.0", "--port", "3000"]

FROM dependencies AS build
COPY ./ ./
RUN yarn build

FROM nginx:1 AS prod
COPY ./docker/nginx.conf /etc/nginx/conf.d/default.conf
HEALTHCHECK \
  --interval=30s \
  --retries=5 \
  --start-period=120s \
  --start-interval=1s \
  CMD ["curl", "--fail", "http://localhost/healthy"]
COPY --from=build /usr/src/app/dist/ /usr/share/nginx/html/
