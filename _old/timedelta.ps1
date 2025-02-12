#this calculates the time delta between race finishers
#timedelta is compared with race WINNER, not with the car ahead
#actual delta is difference between delta times!

param(
    $result = '.\iracing_result\iracing-result-71533771.json'
)

$resultjson = get-content $result
$result = $resultjson | ConvertFrom-Json

$session_results = $result.session_results.where{$_.simsession_name -like "RACE"}.results
$car_classes = $session_results.car_class_name | Select-Object -Unique


$class_results = $session_results.where{$_.car_class_name -like "GTP"}
$race_winner = $class_results.where{$_.finish_position_in_class -eq 0}
$race_totaltime = ($race_winner.average_lap * $race_winner.laps_complete)

$final_result_col_gtp = @()
foreach ($session_result in $class_results){
    $car_number = $session_result.livery.car_number
    if ($session_result.average_lap -gt 0) {
        $behindlaps = $race_totaltime / $session_result.average_lap
    }else{
        $behindlaps = 0
    }
    $factor = $session_result.average_lap/$race_winner.average_lap
    $behindtime = ($factor * $race_totaltime)
    $timedelta = $behindtime - $race_totaltime
    $final_result = $session_result | select car_class_name,finish_position_in_class,display_name #,finish_position_in_class
    $final_result | add-member -NotePropertyName car_number -NotePropertyValue $car_number -Force
    $final_result | add-member -NotePropertyName laps -NotePropertyValue ([math]::round($behindlaps,2)) -Force
    $final_result | add-member -NotePropertyName time -NotePropertyValue ([math]::round(($behindtime/10000),2)) -Force
    $final_result | add-member -NotePropertyName timedelta -NotePropertyValue ([math]::round(($timedelta/10000),2)) -Force
    $final_result_col_gtp += $final_result
}

$final_result_col_gtp | ft
$final_result_col_gtp | Export-Csv -path .\result_gtp_timedelta.csv -NoTypeInformation -UseCulture 

$class_results = $session_results.where{$_.car_class_name -like "IMSA23"}
$race_winner = $class_results.where{$_.finish_position_in_class -eq 0}
$race_totaltime = ($race_winner.average_lap * $race_winner.laps_complete)

$final_result_col_gt3  = @()
foreach ($session_result in $class_results){
    $car_number = $session_result.livery.car_number
    if ($session_result.average_lap -gt 0) {
        $behindlaps = $race_totaltime / $session_result.average_lap
    }else{
        $behindlaps = 0
    }
    $factor = $session_result.average_lap/$race_winner.average_lap
    $behindtime = ($factor * $race_totaltime)
    $timedelta = $behindtime - $race_totaltime
    $final_result = $session_result | select car_class_name,finish_position_in_class, display_name #,finish_position_in_class
    $final_result | add-member -NotePropertyName car_number -NotePropertyValue $car_number -Force
    $final_result | add-member -NotePropertyName laps -NotePropertyValue ([math]::round($behindlaps,2)) -Force
    $final_result | add-member -NotePropertyName time -NotePropertyValue ([math]::round(($behindtime/10000),2)) -Force
    $final_result | add-member -NotePropertyName timedelta -NotePropertyValue ([math]::round(($timedelta/10000),2)) -Force
    $final_result_col_gt3 += $final_result
}

$final_result_col_gt3 | ft
$final_result_col_gt3 | Export-Csv -path .\result_gt3_timedelta.csv -NoTypeInformation -UseCulture