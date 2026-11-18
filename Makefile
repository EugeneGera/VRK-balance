.PHONY: start stop start-full start-experiment
start:
	python3 scripts/start.py
stop:
	python3 scripts/start.py --stop
start-full:
	python3 scripts/start.py --quality
start-experiment:
	python3 scripts/start.py --experiment

build-dev:
	docker compose -f docker-compose.dev.yaml up --build -d
	docker exec -i bcp_PGDB psql -U postgres -d balance_comission < BK.sql
	docker exec -i bcp_backend mkdir uploads
	docker-compose -f docker-compose.dev.yaml logs --follow
dump-db:
	docker exec -t bcp_PGDB pg_dumpall -c -U postgres > BK_`date +%Y-%m-%d"_"%H_%M_%S`.sql
down-dev:
	docker compose -f docker-compose.dev.yaml down
psql-db:
	docker exec -it bcp_PGDB psql -U postgres -d balance_comission
update-scripts:
	docker cp ./backend/app/src/. bcp_backend:/backend/app/src/
update-db:
	docker exec -i bcp_PGDB bash -c "psql -U postgres -c \"SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = 'balance_comission' AND pid <> pg_backend_pid();\" -c \"DROP DATABASE IF EXISTS balance_comission;\" -c \"CREATE DATABASE balance_comission;\""
	docker exec -i bcp_PGDB psql -U postgres -d balance_comission < BK.sql
