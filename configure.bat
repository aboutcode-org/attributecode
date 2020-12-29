@echo OFF
@setlocal
@rem Copyright (c) nexB Inc. http://www.nexb.com/ - All rights reserved.

@rem ################################
@rem # A configuration script for Windows
@rem #
@rem # The options and (optional) arguments are:
@rem #  --clean : this is exclusive of anything else and cleans the environment
@rem #    from built and installed files
@rem #
@rem #  --python < path to python.exe> : this must be the first argument and set
@rem #    the path to the Python executable to use. If < path to python.exe> is
@rem #    set to "path", then the executable will be the python.exe available
@rem #    in the PATH.
@rem #
@rem #  <some conf path> : this must be the last argument and sets the path to a
@rem #    configuration directory to use.
@rem ################################

@rem ################################
@rem # Defaults. Change these variables to customize this script locally
@rem ################################
@rem # you can define one or more thirdparty dirs, each where the variable name
@rem # is prefixed with TPP_DIR
set "TPP_DIR=thirdparty"

@rem # default configurations
set "CONF_DEFAULT=etc/conf"

@rem # default supported version for Python 3 
set SUPPORTED_PYTHON3=3.6

@rem #################################

@rem python --version
@rem python -c "import sys;print(sys.executable)"


@rem Current directory where this .bat files lives
set CFG_ROOT_DIR=%~dp0

@rem path where a configured Python should live in the current virtualenv if installed
set CONFIGURED_PYTHON=%CFG_ROOT_DIR%bin\python.exe

set PYTHON_EXECUTABLE=

@rem parse command line options and arguments 
:collectopts
if "%1" EQU "--help" (goto cli_help)
if "%1" EQU "--clean" (set CFG_CMD_LINE_ARGS=--clean) && goto find_python
if "%1" EQU "--python" (set PROVIDED_PYTHON=%~2) && shift && shift && goto collectopts

@rem We are not cleaning: Either we have a provided configure config path or we use a default.
if ""%1""=="""" (
    set CFG_CMD_LINE_ARGS=%CONF_DEFAULT%
) else (
    set CFG_CMD_LINE_ARGS=%1
)

@rem If we have a pre-configured Python in our virtualenv, reuse this as-is and run
if exist ""%CONFIGURED_PYTHON%"" (
    set PYTHON_EXECUTABLE=%CONFIGURED_PYTHON%
    goto run
)

@rem If we have a command arg for Python use this as-is
if ""%PROVIDED_PYTHON%""==""path"" (
    @rem use a bare python available in the PATH
    set PYTHON_EXECUTABLE=python
    goto run
)
if exist ""%PROVIDED_PYTHON%"" (
    set PYTHON_EXECUTABLE=%PROVIDED_PYTHON%
    goto run
)


@rem otherwise we search for a suitable Python interpreter
:find_python

@rem First check the existence of the "py" launcher (available in Python 3)
@rem if we have it, check if we have a py -3 installed with the good version or a py 2.7
@rem if not, check if we have an old py 2.7
@rem exist if all fails

where py >nul 2>nul
if %ERRORLEVEL% == 0 (
    @rem we have a py launcher, check for the availability of our required Python 3 version
    py -3.6 --version >nul 2>nul
    if %ERRORLEVEL% == 0 (
        set PYTHON_EXECUTABLE=py -3.6
    ) else (
        @rem we have py and no python 3, exit
        echo * Unable to find an installation of Python.
        exit /b 1
    )
) else (
    @rem we have no py launcher
    echo * Unable to find an installation of Python.
    exit /b 1
)

:run

@rem without this things may not always work on Windows 10, but this makes things slower
set PYTHONDONTWRITEBYTECODE=1

call %PYTHON_EXECUTABLE% "%CFG_ROOT_DIR%etc\configure.py" %CFG_CMD_LINE_ARGS%

@rem Return a proper return code on failure
if %ERRORLEVEL% neq 0 (
    exit /b %ERRORLEVEL%
)
endlocal

