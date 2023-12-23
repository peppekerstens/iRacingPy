$member_data = import-csv -Path .\member_data.csv

$resultjson = get-content .\iracing_result\iracing-result-65397658.json
$result = $resultjson | ConvertFrom-Json



$session_results = $result.session_results.where{$_.simsession_name -like "RACE"}.results

$result = @()
foreach ($session_result in $session_results){
    $drivers = $session_result.driver_results
    $car_class = $session_result.car_class_name
    foreach ($driver in $drivers){
        $founddriver = $member_data.where{$_.cust_id -eq $driver.cust_id}
        $founddriver | add-member -NotePropertyName car_class_name -NotePropertyValue $car_class -Force
        $result += $founddriver
    }
}

$result |ft
