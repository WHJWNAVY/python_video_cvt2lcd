@echo off
:start_qrcode
set cur_path="%cd%\py_video_to_lcd_2bit.py"
python %cur_path%
rem pause
goto start_qrcode: