# Windows-only: verify the copy retains a genuine ACE file but no inventoried artifacts.
param([Parameter(Mandatory=$true)][string]$TemplateDir)
$ErrorActionPreference='Stop'
$checks=@(
    @{File='Lithos_GURBELEN18_Bos.accdb'; Tables=@('ÖZELLİKLER','ÇEKİRDEKLER','MAKROLİTLER','MİKROLİT')},
    @{File='Lithos_GURBELEN18_Bos_EN.accdb'; Tables=@('Features','Cores','Macroliths','Microliths')}
)
$dao=$null
try {
    $dao=New-Object -ComObject 'DAO.DBEngine.120'
    foreach($check in $checks) {
        $p=Join-Path $TemplateDir $check.File
        if(-not (Test-Path -LiteralPath $p -PathType Leaf)){ throw "Missing template: $p" }
        $db=$null
        try {
            $db=$dao.OpenDatabase($p,$false,$true)
            foreach($tablename in $check.Tables) {
                $safe=$tablename.Replace(']',']]')
                $r=$null
                try {
                    $r=$db.OpenRecordset("SELECT COUNT(*) AS N FROM [$safe]",4)
                    $count=[int]$r.Fields.Item(0).Value
                    if($count -ne 0){ throw "Template is not blank: $($check.File), $tablename has $count records" }
                } finally { if($r){$r.Close()} }
            }
        } finally { if($db){$db.Close()} }
    }
    Write-Output 'PASS: TR and EN inventory tables are empty'
    exit 0
} catch {
    Write-Error "ACCESS VERIFICATION FAILED: $($_.Exception.Message)"
    exit 1
}
