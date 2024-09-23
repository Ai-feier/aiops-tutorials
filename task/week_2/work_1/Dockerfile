FROM golang:1.22.5-alpine AS builder

RUN apk add --no-cache git

WORKDIR /app

COPY . .

RUN go mod download
RUN CGO_ENABLED=0 go build -o main .

FROM alpine:3.18

WORKDIR /app

RUN apk add --no-cache ca-certificates && apk add --no-cache tzdata && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

COPY --from=builder /app/main /app/

CMD ["/app/main"]