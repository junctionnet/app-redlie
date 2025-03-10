.PHONY: install deploy dev production db clean apply plan offline
.DEFAULT_GOAL := deploy-dev


install-clean: clean-node-modules clean-serverless git-submodules
	@echo "Installing dependencies"
	git submodule update --remote --recursive
	npm install -g serverless@3.38.0
	npm install

install:
	@echo "Installing dependencies"
	git submodule update --remote --recursive
	npm install -g serverless@3.38.0
	npm install

deploy:
	@echo "Deploying with stage: $(ENV)"
	export STAGE=$(ENV) && \
    export REGION=us-east-1 && \
	serverless deploy --verbose --stage $(ENV)

remove:
	@echo "Removing $(NAME)"
	sh infrastructure/bin/remove-mappings.sh $(NAME) entrywriter
	export STAGE=$(NAME) && serverless remove --stage $(NAME) --region us-east-1 --verbose

run:
	@echo "Serverless Offline"
	export STAGE=dev && \
	export LOCAL=1 && \
	export REGION=us-east-1 && \
	export SLS_DEBUG=* && \
	serverless offline --inspect

test-api-dev:
	@echo "Running API tests"
	export STAGE=dev && \
    export REGION=us-east-1 && \
	pytest tests/test_api*

db-migrations:
	@echo "Running db migrations"
	alembic upgrade head

apply: clean-terraform
	@echo "Terraform Apply"
	export REGION=us-east-1 && \
	cd ./infrastructure/live/$(ENV)/$(COMPONENT) && \
	terragrunt init && \
	terragrunt apply --auto-approve --terragrunt-non-interactive
	cd --

plan: clean-terraform
	@echo "Terraform Apply"
	export REGION=us-east-1 && \
	cd ./infrastructure/live/$(ENV)/$(COMPONENT) && \
	terragrunt init && \
	terragrunt plan
	cd --

invoke:
	@echo "Invoking function"
	export STAGE=$(ENV) && \
    export REGION=us-east-1 && \
	serverless invoke --function $(FUNCTION) --stage $(ENV) #--path tests/event.json

logs:
	@echo "Getting logs"
	serverless logs -f $(FUNCTION) --tail


api-mappings:
	@echo "Creating API mappings"
	sh infrastructure/bin/api-mappings/issuers.sh $(ENV)
	sh infrastructure/bin/api-mappings/admin.sh $(ENV)
	sh infrastructure/bin/api-mappings/connector.sh $(ENV)

git-submodules:
	@echo "Updating git submodules"
	rm -rf src/common
	git submodule update --init --recursive

clean-terraform:
	find . -type d -name ".terragrunt-cache" -prune -exec rm -rfv {} \;

clean-serverless:
	rm -rf .serverless

clean-node-modules:
	rm -rf node_modules


dev:
	$(MAKE) git-submodules
	$(MAKE) deploy ENV=dev

production:
	$(MAKE) deploy ENV=production



remove-dev:
	$(MAKE) remove NAME=dev




invoke-db-migrations-dev:
	@echo "Running db migrations"
	$(MAKE) invoke ENV=dev FUNCTION=AlembicDbMigrations

invoke-db-migrations-production:
	@echo "Running db migrations"
	$(MAKE) alembic-db-migrations ENV=production



apply-infra-dev:
	$(MAKE) apply ENV=dev COMPONENT=api-resources

apply-infra-production:
	$(MAKE) apply ENV=production COMPONENT=api-resources



logs-all:
	@echo "Getting logs"
	$(MAKE) logs FUNCTION=muestras && \
	$(MAKE) logs FUNCTION=muestrasEvents