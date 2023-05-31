SETLOCAL
SET PROJECT_DIR=%cd%
SET PROJECT_NAME=cookiecutter-spatial-data-science

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: COMMANDS                                                                     :
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

:: Jump to command
GOTO %1

:: Build the local environment from the environment file
:env
    ENDLOCAL & (

        :: Create environment
        CALL python -m venv env

        :: Activate the environment
        CALL env/Scripts/activate

        :: Install requirements
        CALL pip install -r requirements.txt

    )
    EXIT /B