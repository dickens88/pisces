FROM node:18-alpine AS builder

WORKDIR /app

COPY package.json ./

RUN npm cache clean --force

COPY package-lock.json* ./

RUN npm ci --legacy-peer-deps || \
    (rm -f package-lock.json && npm install --legacy-peer-deps)

COPY . .

RUN npm run prod

FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

