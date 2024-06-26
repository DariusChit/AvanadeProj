FROM node:18-alpine AS base

RUN apk add --no-cache g++ make py3-pip libc6-compat
WORKDIR /app
COPY frontend/package*.json ./
EXPOSE 3000


FROM base as builder
WORKDIR /app
COPY ./frontend .
RUN npm run build

FROM base as production
WORKDIR /app

ENV NODE_ENV=production
RUN npm ci

RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001
USER nextjs

COPY --from=builder --chown=nextjs:nodejs /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/public ./public

CMD ["npm", "start"]

FROM base as dev
ENV NODE_ENV=development
RUN npm install
RUN npm ci
RUN rm -fr /app/.next
COPY frontend/. .
CMD ["npm", "run", "dev"]
