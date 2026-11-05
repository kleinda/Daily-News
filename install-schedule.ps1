# רישום משימות ב-Windows Task Scheduler:
#   1. DailyNews-Agent  - מריץ את הסוכן כל יום ב-08:00 (גם אם המחשב היה כבוי - ירוץ כשיידלק)
#   2. DailyNews-Server - מפעיל את שרת האתר ברקע בכל כניסה ל-Windows (http://localhost:8000)
# הרצה:  powershell -ExecutionPolicy Bypass -File install-schedule.ps1
# הסרה:  Unregister-ScheduledTask DailyNews-Agent, DailyNews-Server -Confirm:$false

$dir = $PSScriptRoot
$pythonw = (Get-Command pythonw.exe -ErrorAction Stop).Source
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopIfGoingOnBatteries -AllowStartIfOnBatteries -ExecutionTimeLimit 0

$agent = New-ScheduledTaskAction -Execute $pythonw -Argument "`"$dir\agent.py`"" -WorkingDirectory $dir
Register-ScheduledTask -TaskName "DailyNews-Agent" -Action $agent -Settings $settings -Force `
  -Trigger (New-ScheduledTaskTrigger -Daily -At "08:00") | Out-Null

$server = New-ScheduledTaskAction -Execute $pythonw -Argument "`"$dir\server.py`" --no-browser" -WorkingDirectory $dir
Register-ScheduledTask -TaskName "DailyNews-Server" -Action $server -Settings $settings -Force `
  -Trigger (New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME) | Out-Null

Start-ScheduledTask -TaskName "DailyNews-Server"
Write-Host "Scheduled: DailyNews-Agent (daily 08:00), DailyNews-Server (at logon). Site: http://localhost:8000"
