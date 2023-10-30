NAME = inquisitor

all: help

help:
	@ echo "\033[0;31m  You need help ? Try with one of these commands :\033[0;39m"
	@ echo ""
	@ awk 'BEGIN {FS = ":.*##";} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
	@ echo ""

up-demo: ## Start the demo
	@ docker compose -f ./demo/docker-compose.yml up -d
	@ ./scripts/show-arp.sh

run-inquisitor: ## Run the inquisitor
	@ docker exec -it demo-inquisitor-1 python3 /home/inquisitor.py $(shell ./scripts/getArgs.sh)

run-inquisitor-v: ## Run the inquisitor in verbose mode
	@ docker exec -it demo-inquisitor-1 python3 /home/inquisitor.py -v $(shell ./scripts/getArgs.sh)

show-arp: ## Show the arp table, ip and mac address
	./scripts/show-arp.sh

down-demo: ## Stop the demo
	@ docker compose -f ./demo/docker-compose.yml down

logs-demo: ## Show the logs of the demo
	@ docker compose -f ./demo/docker-compose.yml logs

reload-demo: ## Reload the demo
	@ docker compose -f ./demo/docker-compose.yml up --build

status: ## Show the status of the containers
	@ docker ps

clean: down-demo ## Clean the docker system
	@ docker system prune -f

prune: down-demo ## Prune the docker system
	@ docker system prune -a

fclean: down-demo prune ## Clean and prune the docker system
	@ docker system prune -af

.PHONY:
