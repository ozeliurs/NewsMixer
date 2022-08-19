# NewsMixer

## Usage

### Docker

`docker run -p 80:8000 -v <path>:/app/persistent:rw ozeliurs/news-mixer:latest`

### Docker Compose

```yaml
version: '3'
services:
  web:
    image: ozeliurs/news-mixer:latest
    container_name: news-mixer
    restart: unless-stopped
    volumes:
      - <path>:/app/persistent:rw
    networks:
      - proxy
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.news-mixer.entrypoints=http"
      - "traefik.http.routers.news-mixer.rule=Host(`nm.ozeliurs.com`)"
      - "traefik.http.middlewares.news-mixer-https-redirect.redirectscheme.scheme=https"
      - "traefik.http.routers.news-mixer.middlewares=news-mixer-https-redirect"
      - "traefik.http.routers.news-mixer-secure.entrypoints=https"
      - "traefik.http.routers.news-mixer-secure.rule=Host(`nm.ozeliurs.com`)"
      - "traefik.http.routers.news-mixer-secure.tls=true"
      - "traefik.http.routers.news-mixer-secure.tls.certresolver=http"
      - "traefik.http.routers.news-mixer-secure.service=news-mixer"
      - "traefik.http.services.news-mixer.loadbalancer.server.port=8000"
      - "traefik.docker.network=proxy"

networks:
  proxy:
    external: true
```
