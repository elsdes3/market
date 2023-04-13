#################################################################################
# GLOBALS                                                                       #
#################################################################################

#################################################################################
# COMMANDS                                                                      #
#################################################################################

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

## Run prepare service
prepare:
	@echo "+ $@"
	@docker compose up prepare --detach
.PHONY: prepare

## Run eda service
eda:
	@echo "+ $@"
	@docker compose up eda --detach
.PHONY: eda

## Run transform service
transform:
	@echo "+ $@"
	@docker compose up transform --detach
.PHONY: transform

## Run development service
development:
	@echo "+ $@"
	@docker compose up development --detach
.PHONY: development

## Run post-process service
post-process:
	@echo "+ $@"
	@docker compose up post-process --detach
.PHONY: post-process

## Run create-audience service
create-audience:
	@echo "+ $@"
	@docker compose up create-audience --detach
.PHONY: create-audience

## Get logs for get-data service
get-data-logs:
	@echo "+ $@"
	@./utils.sh "get-data"
.PHONY: get-data-logs

## Get logs for prepare service
prepare-logs:
	@echo "+ $@"
	@./utils.sh "prepare"
.PHONY: prepare-logs

## Get logs for eda service
eda-logs:
	@echo "+ $@"
	@./utils.sh "eda"
.PHONY: eda-logs

## Get logs for transform service
transform-logs:
	@echo "+ $@"
	@./utils.sh "transform"
.PHONY: transform-logs

## Get logs for development service
development-logs:
	@echo "+ $@"
	@./utils.sh "development"
.PHONY: development-logs

## Get logs for post-process service
post-process-logs:
	@echo "+ $@"
	@./utils.sh "post-process"
.PHONY: post-process-logs

## Get logs for create-audience service
create-audience-logs:
	@echo "+ $@"
	@./utils.sh "create-audience"
.PHONY: create-audience-logs

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

## Reset prepare service
reset-prepare:
	@echo "+ $@"
	@./utils.sh "reset-prepare"
.PHONY: reset-prepare

## Reset eda service
reset-eda:
	@echo "+ $@"
	@./utils.sh "reset-eda"
.PHONY: reset-eda

## Reset transform service
reset-transform:
	@echo "+ $@"
	@./utils.sh "reset-transform"
.PHONY: reset-transform

## Reset development service
reset-development:
	@echo "+ $@"
	@./utils.sh "reset-development"
.PHONY: reset-development

## Reset post-process service
reset-post-process:
	@echo "+ $@"
	@./utils.sh "reset-post-process"
.PHONY: reset-post-process

## Reset create-audience service
reset-create-audience:
	@echo "+ $@"
	@./utils.sh "reset-create-audience"
.PHONY: reset-create-audience

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
