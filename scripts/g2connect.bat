:: Windows Batch file to run g2connect
::
:: Supply config.yml file as the command-line argument, e.g.:
::   g2connect config.yml
::
@ECHO off
IF "%1"=="" (
    ECHO Error: Please supply configuration file name
) ELSE (
    IF "%1"=="help" (
        ECHO Usage: %0 [config_filename]
    ) ELSE (
        IF EXIST "%1" (
            python %CONDA_PREFIX%\Scripts\g2connect -f %1
        ) ELSE (
            ECHO Error: File "%1" does not exist
        )
    )
)
