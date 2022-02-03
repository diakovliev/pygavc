@call %~dp0/python_env.bat

pip install -r requirements.txt
rem pip freeze > requirements.txt
python %*