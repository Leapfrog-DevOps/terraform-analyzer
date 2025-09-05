# Define variables for generating files
BACKEND_CONFIG ?= backend.hcl
BACKEND_TPL    ?= backend.hcl.tpl

# Generates TF var file
TF_VAR_CONFIG ?= terraform.tfvars
TF_VAR_TPL ?= terraform.tfvars.tpl

ENV_VARS = $(AWS_REGION) $(ENVIRONMENT)

.PHONY: help
help: ## Display this help message
	@echo "Usage: make [target]"
	@echo
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

.PHONY: init
init: ## Initialize Terraform backend
	@if [ -z "$(AWS_REGION)" ] || [ -z "$(ENVIRONMENT)" ]; then \
		echo "Error: Required environment variables are not set"; \
		exit 1; \
	fi; \
	envsubst < $(BACKEND_TPL) > $(BACKEND_CONFIG); \
	cat $(BACKEND_CONFIG);
	@echo ""
	@echo "Terraform initialization complete."

.PHONY: prepare
prepare: ## Prepares tf var file for every environment
	@if [ -z "$(AWS_REGION)" ] || [ -z "$(ENVIRONMENT)" ] || [ -z "$(DEPLOY_LAMBDA)" ]; then \
		echo "Error: Required environment variables are not set"; \
		exit 1; \
	fi; \
	envsubst < $(TF_VAR_TPL) > $(TF_VAR_CONFIG); \
	cat $(TF_VAR_CONFIG);
	@echo ""
	@echo "Variable initialization complete."
