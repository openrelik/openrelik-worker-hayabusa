### OpenRelik worker for running Hayabusa on input files

### Installation instructions
Add to your docker-compose configuration:

```
  openrelik-worker-hayabusa:
    container_name: openrelik-worker-hayabusa
    image: ghcr.io/openrelik/openrelik-worker-hayabusa:${OPENRELIK_WORKER_HAYABUSA_VERSION}
    restart: always
    environment:
      - REDIS_URL=redis://openrelik-redis:6379
    volumes:
      - ./data:/usr/share/openrelik/data
    command: "celery --app=src.app worker --task-events --concurrency=4 --loglevel=INFO -Q openrelik-worker-hayabusa"
```
