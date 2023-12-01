$resultjson = get-content .\iracing_result\iracing-result-65014840.json
$result = $resultjson | ConvertFrom-Json

$session_results = $result.session_results.where{$_.simsession_name -like "RACE"}.results
#$class_results = $session_results.where{$_.car_class_name -like "GTP"}
$class_results = $session_results.where{$_.car_class_name -like "IMSA23"}
$race_winner = $class_results.where{$_.finish_position_in_class -eq 0}
$race_totaltime = ($race_winner.average_lap * $race_winner.laps_complete)

$final_result_col = @()
foreach ($session_result in $class_results){
    $car_number = $session_result.livery.car_number
    $behindlaps = $race_totaltime / $session_result.average_lap
    $factor = $session_result.average_lap/$race_winner.average_lap
    $behindtime = ($factor * $race_totaltime)
    $timedelta = $behindtime - $race_totaltime
    $final_result = $session_result | select car_class_name,display_name #,finish_position_in_class
    $final_result | add-member -NotePropertyName car_number -NotePropertyValue $car_number -Force
    $final_result | add-member -NotePropertyName laps -NotePropertyValue ([math]::round($behindlaps,2)) -Force
    $final_result | add-member -NotePropertyName time -NotePropertyValue ([math]::round(($behindtime/10000),2)) -Force
    $final_result | add-member -NotePropertyName timedelta -NotePropertyValue ([math]::round(($timedelta/10000),2)) -Force
    $final_result_col += $final_result
}

$final_result_col | ft