SETLOCAL
SET PROJECT_DIR=%cd%

CALL "%PROJECT_DIR%\..\env\Scripts\activate"

CALL python "%PROJECT_DIR%\retrieve_availability.py"