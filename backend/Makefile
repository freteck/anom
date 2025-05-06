run:
	uvicorn backend:app --reload

start-docker:
	docker compose -f ./docker-compose-expose.yml up --detach --build

start-docker-mac:
	docker compose -f ./docker-compose-expose-mac.yml up --detach --build

stop-docker:
	docker compose -f ./docker-compose-expose.yml down

stop-docker-mac:
	docker compose -f ./docker-compose-expose-mac.yml down --remove-orphans
