bronze layer:

compose up: docker-compose up -d
compose up redis only: docker-compose up -d redis db
restart acorn_worker: docker-compose restart acorn_worker

enqueue jobs: docker-compose exec ttb_worker python enqueue_jobs.py
live logs: docker-compose logs -f ttb_worker

degree explorer cookie timeout sequence
docker-compose stop acorn_worker
UPDATE COOKIE IN .env
docker-compose up -d --force-recreate acorn_worker
docker-compose exec acorn_worker rq requeue --all --queue acorn_queue