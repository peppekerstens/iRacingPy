param(
    $resultfile = '.\iracing_result\iracing-result-71133525.json' 
)
$result = get-content $resultfile | ConvertFrom-Json

$session_results = $result.session_results.where{$_.simsession_name -like "RACE"}.results
#$driver_results = $session_results.driver_results

function is_allowed_gtp{
    param($irating)
    return ($irating -gt 2750)
}

function is_allowed_gt3{
    param($irating)
    return ($irating -gt 1700)
}

function is_allowed_lmp2{
    param($irating)
    return ($irating -gt 2000)
}

function get-qualification{
    param($irating)
    if ($irating -ge 2750){return 'gtp'}
    if ($irating -ge 1700){return 'gt3'}
    if ($irating -lt 1700){return 'none'}
}

function get_gt3_AM_classification{
    param($irating)
    if ($irating -ge 3750){return 'no'}
    if ($irating -ge 2750){return 'Gold'}
    if ($irating -lt 2750){return 'Silver'}
}

$result = @()
foreach ($session_result in $session_results){
    $drivers = $session_result.driver_results
    $car_class = $session_result.car_class_name
    $team_name = $session_result.display_name
    $car_number = $session_result.livery.car_number
    foreach ($driver in $drivers){

        $qualification = get-qualification  $driver.oldi_rating
        
        $result += [PSCustomObject]@{
            cust_id = $driver.cust_id
            display_name = $driver.display_name
            team_name = $team_name
            irating = $driver.oldi_rating
            car_clas_name = $car_class
            allowed_car_class = $qualification
            gt3_classification = get_gt3_AM_classification $driver.oldi_rating
            car_number = $car_number
        }
    }
}

$result |ft
$result | Export-Csv -path .\driver_qualification.csv -NoTypeInformation -UseCulture