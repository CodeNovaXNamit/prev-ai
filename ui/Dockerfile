FROM node:20-alpine AS deps

WORKDIR /app

COPY ui/package*.json ./
RUN npm ci

FROM node:20-alpine AS dev

WORKDIR /app

COPY ui/package*.json ./
RUN npm install

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--hostname", "0.0.0.0", "--port", "3000"]

FROM deps AS prod

WORKDIR /app

COPY ui ./
RUN npm run build

EXPOSE 3000

CMD ["npm", "run", "start", "--", "--hostname", "0.0.0.0", "--port", "3000"]
