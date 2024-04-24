for /f "tokens=1-4 delims=/ " %%i in ("%date%") do (
    set month=%%j
    set day=%%k
    set year=%%l
)
SET datestr=%day%_%month%_%year%
SET filename=../log/log-%datestr%.txt
