#this calculates the time delta between race finishers
#timedelta is compared with race WINNER, not with the car ahead
#actual delta is difference between delta times!

param(
    $result = '.\iracing-result-72608683.json'
)

$resultjson = get-content $result
$result = $resultjson | ConvertFrom-Json

$race_results = $result.session_results.where{$_.simsession_name -like "RACE"}.results
$car_classes = $race_results.car_class_name | Select-Object -Unique
$race_winner = $race_results.where{$_.finish_position -eq 0}
$race_total_time = ($race_winner.average_lap * $race_winner.laps_complete)
$race_max_laps = $race_winner.laps_complete

Write-Verbose -Message "Race winner is: $($race_winner.display_name)" -Verbose

$final_result_col = @()
foreach ($car_class in $car_classes){
    Write-Verbose -Message "Processing car class: $($car_class)" -Verbose
    $class_results = $race_results.where{$_.car_class_name -like $car_class}
    $class_winner = $class_results.where{$_.finish_position_in_class -eq 0}
    $class_total_time = ($class_winner.average_lap * $class_winner.laps_complete)
    $class_max_laps = $class_winner.laps_complete
    #$class_max_laps = (Measure-Object $class_results.laps_complete -Maximum).Maximum
    Write-Verbose -Message "Car class winner: $($class_winner.display_name)" -Verbose

    foreach ($car_result in $class_results){
        Write-Verbose -Message "Processing $($car_class) $($car_result.display_name)" -Verbose
        $car_number = $car_result.livery.car_number
        $car_total_time = ($car_result.average_lap * $class_max_laps)

        $time_delta = $car_total_time - $class_total_time #only race winner should have delta of 0, others should be slower
        $final_result = $car_result | select car_class_name,finish_position_in_class,display_name,laps_complete
        $final_result | add-member -NotePropertyName car_number -NotePropertyValue $car_number -Force
        $final_result | add-member -NotePropertyName car_total_time -NotePropertyValue ([math]::round(($car_total_time/10000),2)) -Force
        $final_result | add-member -NotePropertyName class_total_time -NotePropertyValue ([math]::round(($class_total_time/10000),2)) -Force
        $final_result | add-member -NotePropertyName time_delta -NotePropertyValue ([math]::round(($time_delta/10000),2)) -Force
        $final_result_col += $final_result
    }
}
$final_result_col | Export-Csv -path .\result_timedelta.csv -NoTypeInformation -UseCulture 