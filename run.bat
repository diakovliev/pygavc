::!/cmd
@call %~dp0python_env.bat

@start /b /wait pip install -r %~dp0requirements.txt
@rem start /b /wait pip freeze > %~dp0requirements.txt
@start /b /wait python %*
