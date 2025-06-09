$signupSheet = import-csv -path .\pecsignup.csv 
$memberData = import-csv -path .\league_roster.csv
$csvteams = "Name,Background color,Text color,Logo URL,Class 1,Class 2,Class 3`n"
$csvdrivers = "iRacing name,iRacing ID,Multicar team background color,Multicar team text color,Multicar team logo url,iRacing car color override,iRacing car number color override,First name override,Last name override,Suffix override,Initials override,iRacing team name override,Multicar team name,Highlight,Club name override,Photo URL,Number URL,Car Url,Class 1,Class 2,Class 3,Birth date,Home town,Driver header,Driver information`n"
foreach ($signup in $signupSheet){
    write-verbose -message "processing $($signup.'Paid')" -verbose
    if ($signup.Paid -ne [string]::Empty){
        write-verbose -message "processing $($signup.'Team name')" -verbose
        $csvteams += "$(($signup.'Team name').trim()),Transparent,Transparent,,$(($signup.'Competition class').trim()),None,None`n"

        $drivers = @()
        if ($signup.'Is team manager a driver of this team?' -eq 'yes'){
            $drivers += [int]($signup.'Team manager iRacing ID')
        }
        $drivers += [int]($signup.'Driver 1 iRacing ID')
        $drivers += [int]($signup.'Driver 2 iRacing ID')
        $drivers += [int]($signup.'Driver 3 iRacing ID')
        $drivers += [int]($signup.'Driver 4 iRacing ID')
        $drivers += [int]($signup.'Driver 5 iRacing ID')
        $drivers += [int]($signup.'Driver 6 iRacing ID')
        $drivers += [int]($signup.'Driver 7 iRacing ID')
        $drivers += [int]($signup.'Driver 8 iRacing ID')

        write-verbose -message "$drivers " -verbose

        $uniqueDrivers = $drivers.where{$_ -ne 0} | Select-Object  -Unique

        foreach ($driver in $uniqueDrivers){
            $display_name = $memberData.where{$_.cust_id -eq $driver}.display_name
            $csvdrivers += "$($display_name),$($driver),Transparent,Transparent,,Transparent,Transparent,,,,,$(($signup.'Team name').trim()),None,None,,,,,$(($signup.'Competition class').trim()),None,None,,,,`n"
        }
    }
}
$csvdrivers | Out-File .\drivers.csv
$csvteams | Out-File .\teams.csv