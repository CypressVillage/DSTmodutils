@echo off

set /p file=json�ļ�:

for %%i in (%file%) do set dirname=%%~dpi

echo �õ��ļ�%file%

dsanimtool "%file%" "%dirname%/"

echo ��ִ��dsanimtool,����ͬ��zip�ļ�

set zipfile=%dirname%
set suffix=".zip"
::echo �뽫���ɵ�%zipfile%%suffix%�ļ��ƶ��� workshop\content\322330\3052181004\anim ��

pause