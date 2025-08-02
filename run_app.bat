@echo off
echo 🎵 Starting Music Recommendation App with Python 3.11...
echo.

REM Activate virtual environment
call venv311\Scripts\activate.bat

REM Verify Python version
python --version

REM Run the Streamlit app
echo.
echo 🚀 Starting Streamlit app...
streamlit run app.py

pause 