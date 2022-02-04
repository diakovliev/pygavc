# Python installer

$script_path=$MyInvocation.MyCommand.Path
$script_dir=Split-Path $script_path -Parent

$python_uri="https://www.python.org/ftp/python/3.9.10/python-3.9.10-embed-amd64.zip"
$pth_file="python39._pth"
$archive="$env:TEMP\python.zip"
$destination_path="$script_dir\_python"
$get_pip_uri="https://bootstrap.pypa.io/get-pip.py"
$scripts_path="$destination_path\Scripts"

# Remove-Item -Path $destination_path -Recurse -Force

Write-Output "Install python distribution '$python_uri' into '$destination_path' ..."

if (Test-Path -Path $destination_path) {
	Write-Output "Destination directory '$destination_path' already exists. Leave."
	exit 0
}

Invoke-WebRequest -Uri $python_uri -OutFile $archive
Expand-Archive -Path $archive -DestinationPath $destination_path
Remove-Item -Path $archive

Write-Output "Python installed into '$destination_path'."
New-Item -ItemType directory $scripts_path

$env:PATH="$destination_path;$scripts_path;" + $env:PATH

Write-Output "Install pip..."
Invoke-WebRequest -Uri $get_pip_uri -OutFile $scripts_path\get-pip.py

python $scripts_path\get-pip.py
Remove-Item -Path $scripts_path\get-pip.py
Remove-Item -Path $destination_path\$pth_file