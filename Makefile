.PHONY: install test run clean install-service uninstall-service setup status

# Development tasks
install:
	pip install -e .

test:
	cd tests && python -m pytest

run:
	python bird_cam.py

clean:
	rm -rf __pycache__
	rm -rf src/__pycache__
	rm -rf src/*/__pycache__
	rm -rf build/
	rm -rf *.egg-info

# System setup and service management
setup:
	bash scripts/install.sh

status:
	bash scripts/status.sh

install-service:
	bash scripts/install.sh
	sudo cp scripts/service/bird_cam.service /etc/systemd/system/
	sudo systemctl daemon-reload
	sudo systemctl enable bird_cam
	sudo systemctl start bird_cam

uninstall-service:
	sudo systemctl stop bird_cam || true
	sudo systemctl disable bird_cam || true
	sudo rm /etc/systemd/system/bird_cam.service || true
	sudo systemctl daemon-reload

# Move to scripts directory
scripts/%.sh:
	cd scripts && ./$(notdir $@) 