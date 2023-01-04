cd "%cd%\\..\\"
python -m venv "translator"
cd translator\\Scripts
pip.exe install pyinstaller
pip.exe install -r "..\\..\\requirements.txt"
cmd /k