# Global variables

## HPC - Instance size options:
### small: 8 cores, 16GB RAM, 1 GPU
### medium: 16 cores, 32GB RAM, 1 GPU
### large: 32 cores, 64GB RAM, 1 GPU
INSTANCE_SIZE=small
## By default, use the following configurations:
MEMORY_RAM=16G
N_vCPU=8
N_GPU=1
PYTHON_INTERPRETER = python3
PROJECT_NAME = oil-spill-SAR

## Delete all compiled Python files and other UNIX-like files
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.out" -delete

## Prepare all data 
# TODO: Add Sentinel-1 calibration steps
.PHONY: data
data: 
	python src/data/make_dataset.py data/unprocessed/mklab data/processed/mklab

## Reformats all Python files using Black
lint:
	black src

## Load dotenv
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

## Sync local reporitory from remote repository using rsync
sync_from_remote: load_dotenv
	@rsync -avz -e "ssh -i $(IDENTITY_FILE)" $(REMOTE_USERNAME)@$(REMOTE_HOSTNAME):$(PROJECT_NAME)/ . \
	--exclude-from=rsync_exclude.txt

## Request to allocate job on High-Performance Computing (HPC) cluster
allocate_job:
	@echo "Requesting allocation for $(INSTANCE_SIZE) size instance..."
ifeq (default,$(INSTANCE_SIZE))
	@salloc -n 1 --mem=$(MEMORY_RAM) -c $(N_vCPU) --gpus=$(N_GPU)
else ifeq (small,$(INSTANCE_SIZE))
	@salloc -n 1 --mem=16G -c 8 --gpus=1
else ifeq (medium,$(INSTANCE_SIZE))
	@salloc -n 1 --mem=32G -c 16 --gpus=1
else ifeq (large,$(INSTANCE_SIZE))
	@salloc -n 1 --mem=64G -c 32 --gpus=1
else
	@echo "Invalid instance size. Please choose from: default, small, medium, large"
endif

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
	@sh ./scripts/enroot/run-mounted.sh oil-spill-SAR
