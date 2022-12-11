#################################################################################
# GLOBALS                                                                       #
#################################################################################

# HPC - Instance size options:
# small: 8 cores, 16GB RAM, 1 GPU (5GB per GPU), 8h runtime, NVIDIA A100 (Dev mode)
# medium: 16 cores, 32GB RAM, 2 GPU (10 GB per GPU), 24h runtime, NVIDIA A100 (Min mode)
# large: 32 cores, 64GB RAM, 2 GPU (20GB per GPU), 48h runtime, NVIDA A100 (Normal mode)
# xlarge: 64 cores, 128GB RAM, 3 GPU (40GB per GPU), 72h runtime, NVIDIA A100 (Max mode)
INSTANCE_SIZE=small
PYTHON_INTERPRETER = python3
PROJECT_NAME = oil-spill-SAR

#################################################################################
# PROJECT VARIABLES                                                             #
#################################################################################
INSTALL_FLEET_LINK=https://download.jetbrains.com/product?code=FLL&release.type=preview&release.type=eap&platform=linux_x64


#################################################################################
# COMMANDS                                                                      #
#################################################################################

## Delete all compiled Python files and other UNIX-like files
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.out" -delete
	find . -type f -name "*.sqsh" -delete

## Prepare all data 
# TO-DO: Add Sentinel-1 calibration steps
.PHONY: data
data: 
	python src/data/make_dataset.py data/unprocessed/mklab data/processed/mklab

## Reformats all Python files using Black
lint:
	black src

# Load dotenv
load_dotenv:
ifneq (,$(wildcard ./.env))
    include .env
    export
endif

## Push all committed files to currently branch
sync_to_git: clean lint
	git push -u origin $(git rev-parse --abbrev-ref HEAD)

## Pull all files from remote repository
sync_from_git:
	git checkout main
	git fetch origin main
	git pull

## Sync local repository with remote repository using rsync
sync_to_remote: load_dotenv
	@rsync -avz -e "ssh -i $(IDENTITY_FILE)" . $(REMOTE_USERNAME)@$(REMOTE_HOSTNAME):$(PROJECT_NAME)/ \
	--exclude-from=rsync_exclude.txt

## Sync local repository from remote repository using rsync
sync_from_remote: load_dotenv
	@rsync -avz -e "ssh -i $(IDENTITY_FILE)" $(REMOTE_USERNAME)@$(REMOTE_HOSTNAME):$(PROJECT_NAME)/ . \
	--exclude-from=rsync_exclude.txt

## Request to allocate job on High-Performance Computing (HPC) cluster. Choose: <small>, <medium>, <large>, or <xlarge>
allocate_job:
	@echo "Requesting allocation for $(INSTANCE_SIZE) size instance..."
ifeq (small,$(INSTANCE_SIZE))
	@salloc -p gpu-dev -n 1 -c 12 --mem=24576M --gres=gpu:a100_1g.5gb:1 --time=08:00:00
else ifeq (medium,$(INSTANCE_SIZE))
	@salloc -p gpu -n 1 -c 16 --mem=32768M --gres=gpu:a100_2g.10gb:1 --time=24:00:00
else ifeq (large,$(INSTANCE_SIZE))
	@salloc -p gpu -n 1 -c 32 --mem=65536M --gres=gpu:a100_3g.20gb:1 --time=24:00:00
else ifeq (xlarge,$(INSTANCE_SIZE))
	@salloc -p gpu-max -n 1 -c 64 --mem=131072M --gres=gpu:a100-sxm4-40gb:1 --time=48:00:00
else
	@echo "Invalid instance size. Please choose from: default, small, medium, large or xlarge"
endif


install_fleet: 
ifeq (, $(shell which fleet))
	@echo -e "JetBrains Fleet was not found in PATH.\nJetBrains Fleet will download.\nInstalling JetBrains Fleet..."
	@curl -LSs $INSTALL_FLEET_LINK --output /usr/local/bin/fleet
	@chmod +x /usr/local/bin/fleet
endif

## Run Fleet
fleet: install_fleet
	@echo "Create an instance to remote development using the latest version of Fleet..."
	@fleet launch workspace -- --auth=accept-everyone --publish --enableSmartMode --projectDir=$(PWD)

## Run VSCode
vscode:
	@echo "Creating an instance to remote development using Visual Studio Code Server..."
	@code-server

## Cancel allocated job on High-Performance Computing (HPC) cluster
cancel_job:
	@echo "Canceling allocated job..."
	@scancel ${SLURM_JOB_ID}

## Build Docker container
build_docker:
	@echo "Building Docker image..."
	@sh ./scripts/docker/build.sh

## Run Docker container
run_docker:
	@echo "Running Docker container..."
	@sh scripts/docker/run.sh

## Build Enroot container
build_enroot:
	@echo "Building Enroot image..."
	@sh ./scripts/enroot/build.sh

## Run Enroot container
run_enroot:
	@echo "Running Enroot container..."
	@sh ./scripts/enroot/run.sh oil-spill-SAR

#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

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
		for (i=1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \ 
	| more $(shell test $(shell uname) = Darwim && echo '--no-init --raw-control-chars')
