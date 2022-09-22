## Delete all compiled Python files
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

## Push all committed files to currently branch
sync_repo_to_git:
	git push -u origin $(git rev-parse --abbrev-ref HEAD)

## Pull all files from remote repository
sync_repo_from_git:
	git checkout main
	git fetch origin main
	git pull
