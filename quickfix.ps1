$resultsjson = get-content c:\users\peppe\downloads\eventresult-74817982.json
$results = $resultsjson | ConvertFrom-Json
$raceresults_section = $results.data.session_results.where{$_.simsession_name -match 'RACE'}
$raceresults = $raceresults_section.results
$raceresults | ft team_id, display_name, car_class_name, position, starting_position, starting_position_in_class, finish_position, finish_position_in_class

foreach ($result in $raceresults){
    if (($result.finish_position -gt 0) -and ($result.finish_position -lt 19)){
        $result.position--
        $result.finish_position--
        $result.finish_position_in_class--
        foreach ($driver in $result.driver_results){
            $driver.position--
            $driver.finish_position--
            $driver.finish_position_in_class-- 
        }
    }elseif ($result.finish_position -eq 0 ){
        $result.position = 18
        $result.finish_position = 18
        $result.finish_position_in_class = 18
        foreach ($driver in $result.driver_results){
            $driver.position = 18
            $driver.finish_position = 18
            $driver.finish_position_in_class = 18
        }
    }
}

$raceresults = $raceresults | Sort-object -property finish_position
$raceresults | ft team_id, display_name, car_class_name, position, starting_position, starting_position_in_class, finish_position, finish_position_in_class

$resultsjson = $results | ConvertTo-Json -Depth 9
$resultsjson | set-content c:\users\peppe\downloads\eventresult-74817982-edt.json