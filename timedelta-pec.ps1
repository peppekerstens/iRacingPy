#this calculates the time delta between race finishers
#timedelta is compared with race WINNER, not with the car ahead
#actual delta is difference between delta times!

param(
    $result = '.\iracing_result\iracing-result-73082774.json'
)

function process_car_class($class_results){
    #as car classes have been sub devided, the finish_position_in_class = 0 is not always valid as being the winner 
    #for some reason measure-object does not work, so code to minimum position
    $class_winner_position = 1000 # unrealistic high beginner value
    $class_results.finish_position_in_class | Foreach-Object { if ($_ -lt $class_winner_position){$class_winner_position = $_}}
    #$class_winner_position = (Measure-Object $class_results.finish_position_in_class -Minimum).Minimum
    #Write-Verbose -Message "Car class winner: $($class_results.finish_position_in_class)" -Verbose
    $class_winner = $class_results.where{$_.finish_position_in_class -eq $class_winner_position}
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
        $final_result
    }
}


$resultjson = get-content $result
$result = $resultjson | ConvertFrom-Json

$race_results = $result.session_results.where{$_.simsession_name -like "RACE"}.results
$car_classes = $race_results.car_class_name | Select-Object -Unique

#for PEC car class can be devided in sub classes, so advanced filter based on car_number as well. 
#however; check for human errors first

$gtp_results = $race_results.where{$_.car_class_name -like 'GTP'}
$gt3_results = $race_results.where{$_.car_class_name -like 'GT3 Class'}
$gt3am_results = $gt3_results.where{$_.livery.car_number -gt 200}
$gt3pro_results = $gt3_results.where{$_.livery.car_number -lt 200}

#$race_winner = $race_results.where{$_.finish_position -eq 0}
#$race_total_time = ($race_winner.average_lap * $race_winner.laps_complete)
#$race_max_laps = $race_winner.laps_complete
#Write-Verbose -Message "Race winner is: $($race_winner.display_name)" -Verbose

$final_result_col = @()
Write-Verbose -Message "Processing car class: GTP" -Verbose
#process_car_class($gtp_results)
$final_result_col += process_car_class($gtp_results)
Write-Verbose -Message "Processing car class: GT3Pro" -Verbose
#process_car_class($gt3pro_results)
$final_result_col += process_car_class($gt3pro_results)
Write-Verbose -Message "Processing car class: GT3Am" -Verbose
#process_car_class($gt3am_results)
$final_result_col += process_car_class($gt3am_results)

$final_result_col | Export-Csv -path .\result_timedelta.csv -NoTypeInformation -UseCulture 