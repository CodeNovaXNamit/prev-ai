FROM node:20-alpine

WORKDIR /app

COPY ui/package*.json ./
RUN npm ci

COPY ui .
RUN npm run build

EXPOSE 3000

CMD ["npm", "run", "start", "--", "--hostname", "0.0.0.0", "--port", "3000"]
