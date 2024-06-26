 #   pmtbase.azurecr.c

clean:
	find . -name '*.py[co]' -delete
	find . -name '__pycache__' -delete
	find . -name '*pid' -delete
	find . -name '*.log' -delete
	rm -rf build dist *egg-info output
	@echo Clean done

venv:
	conda create -n glm-role-play python=3.10.6 -y
	conda activate glm-role-play

pip_install: 
	pip install -r requirements.txt --upgrade pip -i http://pypi.mirrors.ustc.edu.cn/simple/ --trusted-host pypi.mirrors.ustc.edu.cn --default-timeout=100

run:
	python3 cli.py
