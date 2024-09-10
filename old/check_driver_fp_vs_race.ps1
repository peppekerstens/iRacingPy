param(
    $fpdatafile = '.\PEC Season 6 Free Practise times - FP Total.csv'
    ,
    $resultfile = '.\iracing_result\iracing-result-71133525.json'
    ,
    $track = 'Road America'
)

$fp_data = import-csv -Path $fpdatafile
$result = get-content $resultfile | ConvertFrom-Json
$session_results = $result.session_results.where{$_.simsession_name -like "RACE"}.results

$result = @()
foreach ($session_result in $session_results){
    $team_name = $session_result.display_name
    $drivers = $session_result.driver_results
    foreach ($driver in $drivers){
        $founddriver = $fp_data.where{$_.cust_id -eq $driver.cust_id}
        $founddriver | Add-Member -MemberType NoteProperty -Name 'team_name' -Value $team_name
        if ($founddriver){
            $result += $founddriver
        } else {
            Write-Warning "Driver $($driver.cust_id) $($driver.display_name) not found!"
        }
    }
}

$result |ft
$result | Export-Csv -path .\driver_fp_vs_race.csv -NoTypeInformation -UseCulture