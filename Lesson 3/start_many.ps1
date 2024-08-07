# Запуск клієнтських скриптів
$jobs = @()
for ($i = 1; $i -le 50; $i++) {
    Write-Output "Starting client script $i"
    $jobs += Start-Job -ScriptBlock {python "C:\Users\vlady\IdeaProjects\ASYNCHRONUS-HOMEWORK\Lesson 3\meteoclient.py"}
}

# Очікування завершення всіх робіт
$jobs | ForEach-Object { Wait-Job $_ }

# Виведення результатів виконання
$jobs | ForEach-Object {
    Write-Output "Results for job ID $($_.Id):"
    Receive-Job $_
    Remove-Job $_
}