$items = Get-ChildItem -File
$driverName = @()
$winnerNames = @()
foreach ($t in $items){
    $content = get-content $t.fullname
    $results = $content | convertfrom-json
    $winners = $results.session_results.results.where{$_.finish_position -eq 1}
    $winnerNames += $winners.driver_results.display_name
    $driverName += $results.session_results.results.driver_results.display_name
}
$winnerNames = $winnerNames | Select -Unique | Sort-Object 
$winnerNames | Set-Content .\files\winner_names.txt
$driverName = $driverName | Select -Unique | Sort-Object 
"Drivers $($driverName.count)"
"Winnners $($winnerNames.count)"
#$driverName | Set-Content .\driver_names.txt
$commaseperate = [string]::empty
foreach ($item in $commaseperate){
    $commaseperate += "$($item); "
}
$commaseperate | Select -Unique | Set-Content .\files\winner_names.csv #.\driver_names.csv
