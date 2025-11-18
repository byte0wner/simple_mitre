# clean up function after restarting script
function CleanUpSubscribers {
    $sources = "DownloadsFileChanged"

    foreach($source in $sources) {
        if (Get-EventSubscriber -SourceIdentifier $source -ErrorAction SilentlyContinue) {
            Unregister-Event -SourceIdentifier $source -Force
        }
    }
}

CleanUpSubscribers

# folder for monitor
$downloadsFolder = "$env:UserProfile\Downloads"

# init the watcherr
$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $downloadsFolder
$watcher.Filter = "*.*" 
$watcher.IncludeSubdirectories = $false
$watcher.EnableRaisingEvents = $false

# callback function
$action = {
    # if you need you can add here some more extensions
    $filters = ".exe", ".dll", ".msi", ".ps1", ".bat", ".cmd"

    $eventArgs = $event.SourceEventArgs
    $name = $eventArgs.Name
    $fullPath = $eventArgs.FullPath
    $changeType = $eventArgs.ChangeType

    foreach($extension in $filters) {
        if ($fullPath.endswith($extension)) {

            # try to get zone_id 
            $is_zone_id_presented = Get-Item -Path $fullPath -Stream Zone.Identifier -ErrorAction SilentlyContinue
            if ($is_zone_id_presented) {
                $zone_id_content = Get-Content -Path $fullPath -Stream Zone.Identifier
                if ($zone_id_content[1].contains("3")) {
                    # zone_id 4 - unrestricted (file will be blocked)
                    Set-Content -Path $fullPath -Stream Zone.Identifier -Value "[ZoneTransfer]", "ZoneId=4"

                    # get url from zone_id structure
                    Write-Host $fullPath $zone_id_content[2]
                }
            }
        }
    }
}

Register-ObjectEvent $watcher Changed -Action $action -SourceIdentifier "DownloadsFileChanged"

# write some bullshit for user
Write-Host "Monitoring Downloads folder for new files. Press Ctrl+C to stop."


while ($true) {
    Start-Sleep -Seconds 1
}