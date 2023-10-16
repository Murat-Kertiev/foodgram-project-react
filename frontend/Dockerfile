FROM node:13.12.0-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . ./
RUN npx browserslist@latest --update-db
RUN npm run build
CMD cp -r build result_build
