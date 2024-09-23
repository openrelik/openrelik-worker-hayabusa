### OpenRelik worker for running Hayabusa on input files

This worker use the tool `hayabusa` from Yamato-Security.
https://github.com/Yamato-Security/hayabusa for more information.

#### Installation instructions
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

##### Obligatory Fine Print
This is not an official Google product (experimental or otherwise), it is just code that happens to be owned by Google.
