@call %~dp0python_env.bat

pip install -r %~dp0requirements.txt
rem pip freeze > %~dp0requirements.txt
python %*

exit