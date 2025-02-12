$signupSheet = import-csv -path .\ppssignup.csv 

$csvteams = "Name,Background color,Text color,Logo URL,Class 1,Class 2,Class 3`n"
$csvdrivers = "iRacing name,iRacing ID,Multicar team background color,Multicar team text color,Multicar team logo url,iRacing car color override,iRacing car number color override,First name override,Last name override,Suffix override,Initials override,iRacing team name override,Multicar team name,Highlight,Club name override,Photo URL,Number URL,Car Url,Class 1,Class 2,Class 3,Birth date,Home town,Driver header,Driver information`n"
foreach ($signup in $signupSheet){
    if ($signup.Paid -ne [string]::Empty){
        write-verbose -message "processing $($signup.'Team name')" -verbose
        $csvteams += "$(($signup.'Team name').trim()),Transparent,Transparent,,$(($signup.'Competition class').trim()),None,None`n"

        if ($signup.'Driver 1 iRacing ID' -ne [string]::Empty){
            $csvdrivers += "$($signup.'Driver 1 name'),$($signup.'Driver 1 iRacing ID'),Transparent,Transparent,,Transparent,Transparent,,,,,$(($signup.'Team name').trim()),None,None,,,,,$(($signup.'Competition class').trim()),None,None,,,,`n"
        }
        if ($signup.'Driver 2 iRacing ID  (optional)' -ne [string]::Empty){
            $csvdrivers += "$($signup.'Driver 2 name (optional)'),$($signup.'Driver 2 iRacing ID  (optional)'),Transparent,Transparent,,Transparent,Transparent,,,,,$(($signup.'Team name').trim()),None,None,,,,,$(($signup.'Competition class').trim()),None,None,,,,`n"
        }
    }
}
$csvdrivers | Out-File .\ppsdrivers.csv
$csvteams | Out-File .\ppsteams.csv

write-verbose -message "double car number entries" -verbose
$signupSheet.'Car number preference'| Group-Object | Where-Object {$_.Count -gt 1} | Select-Object Name, Count;   
