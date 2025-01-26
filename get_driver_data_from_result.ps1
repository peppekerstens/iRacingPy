param(
    $result = '.\iracing_result\iracing-result-72608683.json'
)

$objresult = get-content $result | ConvertFrom-Json
$race_results = $objresult.session_results.where{$_.simsession_name -like "RACE"}.results

function get-classification{
    param(
        $iRating
    )
    if ($iRating -gt 3500){return 'No'}
    if ($iRating -ge 2750){return 'Gold'}
    return 'Silver'
}

$driverdata = @()
foreach ($session_result in $race_results){
    $drivers = $session_result.driver_results
    $teamid = $session_result.team_id
    $teamname = $session_result.display_name
    $car_class = $session_result.car_class_name
    $car_number = $session_result.livery.car_number
    foreach ($driver in $drivers){
        $gt3am = get-classification $driver.oldi_rating
        $driverdata += [PSCustomObject]@{
            cust_id = $driver.cust_id
            display_name = $driver.display_name
            latest_iRating = $driver.oldi_rating
            car_class_name = $car_class
            car_number = $car_number
            team_id = $teamid
            team_display_name = $teamname
            gtp = $driver.oldi_rating -ge 2750
            lmp2 = $driver.oldi_rating -ge 2000
            gt3pro = $driver.oldi_rating -ge 1700
            gt3am = $gt3am
        }
    }
}


$driverdata | ft
$driverdata | Export-Csv -path .\driver_data.csv -NoTypeInformation -UseCulture