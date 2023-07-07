#################################################################################
# GLOBALS                                                                       #
#################################################################################

#################################################################################
# COMMANDS                                                                      #
#################################################################################

## Remove Python artifacts
clean-py:
	@echo "+ $@"
	@find . -type f -name "*.py[co]" -delete
	@find . -type d -name "__pycache__" -delete
.PHONY: clean-py

## Run lint checks manually
lint:
	@echo "+ $@"
	@if [ ! -d .git ]; then git init && git add .; fi;
	@tox -e lint
.PHONY: lint

## Run get-data service
get-data:
	@echo "+ $@"
	@docker compose up get-data --detach
.PHONY: get-data

## Run train service
train:
	@echo "+ $@"
	@docker compose up train --detach
.PHONY: train

## Run explore service
explore:
	@echo "+ $@"
	@docker compose up explore --detach
.PHONY: explore

## Run upload service
upload:
	@echo "+ $@"
	@docker compose up upload --detach
.PHONY: upload

## Run dash
dash:
	@echo "+ $@"
	@docker compose up dash --detach
.PHONY: dash

## Run dash-auto
dash-auto:
	@echo "+ $@"
	@docker compose -f docker-compose-auto.yml up dash-auto --detach
.PHONY: dash-auto

## Run app service
app:
	@echo "+ $@"
	@docker compose up app --detach
.PHONY: app

## Run cleanup service
cleanup:
	@echo "+ $@"
	@docker compose up cleanup --detach
.PHONY: cleanup

## Get logs for get-data service
get-data-logs:
	@echo "+ $@"
	@./utils.sh "get-data"
.PHONY: get-data-logs

## Get logs for train service
train-logs:
	@echo "+ $@"
	@./utils.sh "train"
.PHONY: train-logs

## Get logs for explore service
explore-logs:
	@echo "+ $@"
	@./utils.sh "explore"
.PHONY: explore-logs

## Get logs for upload service
upload-logs:
	@echo "+ $@"
	@./utils.sh "upload"
.PHONY: upload-logs

## Get logs for dash service
dash-logs:
	@echo "+ $@"
	@./utils.sh "dash"
.PHONY: dash-logs

## Get logs for dash-auto service
dash-auto-logs:
	@echo "+ $@"
	@./utils.sh "dash-auto"
.PHONY: dash-auto-logs

## Get logs for app service
app-logs:
	@echo "+ $@"
	@./utils.sh "app"
.PHONY: app-logs

## Get logs for cleanup service
cleanup-logs:
	@echo "+ $@"
	@./utils.sh "cleanup"
.PHONY: cleanup-logs

## Remove Service(s)
down:
	@echo "+ $@"
	@docker compose down
.PHONY: down

## Remove unused data in Docker
docker-system-prune:
	@echo "+ $@"
	@docker system prune -f
.PHONY: docker-system-prune

## Reset get-data service
reset-get-data:
	@echo "+ $@"
	@./utils.sh "reset-get-data"
.PHONY: reset-get-data

## Reset train service
reset-train:
	@echo "+ $@"
	@./utils.sh "reset-train"
.PHONY: reset-train

## Reset explore service
reset-explore:
	@echo "+ $@"
	@./utils.sh "reset-explore"
.PHONY: reset-explore

## Reset upload service
reset-upload:
	@echo "+ $@"
	@./utils.sh "reset-upload"
.PHONY: reset-upload

## Reset dash service
reset-dash:
	@echo "+ $@"
	@./utils.sh "reset-dash"
.PHONY: reset-dash

## Reset dash-auto service
reset-dash-auto:
	@echo "+ $@"
	@./utils.sh "reset-dash-auto"
.PHONY: reset-dash-auto

## Reset app service
reset-app:
	@echo "+ $@"
	@./utils.sh "reset-app"
.PHONY: reset-app

## Reset cleanup service
reset-cleanup:
	@echo "+ $@"
	@./utils.sh "reset-cleanup"
.PHONY: reset-cleanup

## Run dashboard
manual-dash:
	@echo "+ $@"
	@tox -e dash
.PHONY: manual-dash

## Activate Google Cloud service account
gcloud-auth-login:
	@echo "+ $@"
	@./gcloud_utils.sh "auth-login"
.PHONY: gcloud-auth-login

## Deploy to Google Cloud Run
gcloud-run-deploy:
	@echo "+ $@"
	@./gcloud_utils.sh "run-deploy"
.PHONY: gcloud-run-deploy

## Delete to Google Cloud Run service
gcloud-run-delete:
	@echo "+ $@"
	@./gcloud_utils.sh "run-delete"
.PHONY: gcloud-run-delete

## Run Quarto preview
quarto-preview:
	@echo "+ $@"
	@quarto preview
.PHONY: quarto-preview

## Run Quarto render
quarto-render:
	@echo "+ $@"
	@quarto render
.PHONY: quarto-render

## Run Quarto publish to github pages
quarto-publish:
	@echo "+ $@"
	@quarto publish gh-pages
.PHONY: quarto-publish

#################################################################################
# PROJECT RULES                                                                 #
#################################################################################



#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

# Inspired by <http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html>
# sed script explained:
# /^##/:
# 	* save line in hold space
# 	* purge line
# 	* Loop:
# 		* append newline + line to hold space
# 		* go to next line
# 		* if line starts with doc comment, strip comment character off and loop
# 	* remove target prerequisites
# 	* append hold space (+ newline) to line
# 	* replace newline plus comments by `---`
# 	* print line
# Separate expressions are necessary because labels cannot be delimited by
# semicolon; see <http://stackoverflow.com/a/11799865/1968>
.PHONY: help
help:
	@echo "$$(tput bold)Available rules:$$(tput sgr0)"
	@echo
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| LC_ALL='C' sort --ignore-case \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=19 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| more $(shell test $(shell uname) = Darwin && echo '--no-init --raw-control-chars')
