::!/cmd
@call %~dp0\..\win_python\python_env.bat

@set PYTHONPATH=%PYTHONPATH%;%~dp0

@start /b /wait pip install -r %~dp0tools\requirements.txt
@rem start /b /wait pip freeze > %~dp0tools\requirements.txt
@start /b /wait python %*
