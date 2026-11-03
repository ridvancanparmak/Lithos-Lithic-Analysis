# Lithos v1.2.1 - Create original-schema blank Turkish and English Access databases.
# Both templates derive exclusively from user-selected GURBELEN-18.accdb.
# The original file is opened only as a filesystem COPY and never modified.
# Use descriptive names: PowerShell variables are case-insensitive.
param([string]$OriginalPath='', [string]$OutputDirectory='')
$ErrorActionPreference='Stop'
$Root=$PSScriptRoot
if(-not (Test-Path -LiteralPath (Join-Path $Root 'veri_sozlugu'))){
 $Root=Split-Path -Parent $PSScriptRoot
}
$Templates=if($OutputDirectory){$OutputDirectory}else{Join-Path $Root 'Templates'}
$TurkishTemplatePath=Join-Path $Templates 'Lithos_GURBELEN18_Bos.accdb'
$EnglishTemplatePath=Join-Path $Templates 'Lithos_GURBELEN18_Bos_EN.accdb'
$Audit=Join-Path $Templates 'ACCESS_SABLON_LOG.txt'
$EnglishTableNames=@{'ÖZELLİKLER'='Features';'ÇEKİRDEKLER'='Cores';'MAKROLİTLER'='Macroliths';'MİKROLİT'='Microliths'}
$script:Current='starting'
$createdTR=$false
$createdEN=$false
$db=$null
function Log([string]$msg){Add-Content -LiteralPath $Audit -Encoding UTF8 -Value $msg; Write-Host $msg}
function PropertyValue($field,[string]$name,[string]$default=''){
 try{return [string]$field.Properties.Item($name).Value}catch{return $default}
}
function HasDaoProperty($field,[string]$name){
 for($i=0;$i -lt [int]$field.Properties.Count;$i++){
  if(([string]$field.Properties.Item($i).Name) -ieq $name){return $true}
 }
 return $false
}
function SetCaption($field,[string]$caption){
 if([string]::IsNullOrWhiteSpace($caption)){return}
 if(HasDaoProperty $field 'Caption'){
  $field.Properties.Item('Caption').Value=$caption
 }else{
  $new=$field.CreateProperty('Caption',10,$caption)
  $field.Properties.Append($new)
 }
}
function GetCount($db,[string]$name){
 $escaped=$name.Replace(']',']]')
 $rs=$db.OpenRecordset("SELECT COUNT(*) AS N FROM [$escaped]",4)
 try{return [int]$rs.Fields.Item(0).Value}finally{$rs.Close()}
}
function ValidateCount($db,[bool]$English=$false){
 foreach($name in @('ÖZELLİKLER','ÇEKİRDEKLER','MAKROLİTLER','MİKROLİT')){
  $actualName=if($English){$EnglishTableNames[$name]}else{$name}
  $actual=GetCount $db $actualName
  if($actual -ne 0){throw "Template has remaining records: $name ($actual)"}
 }
}
function ReadAce([string]$p){
 $stream=[IO.File]::OpenRead($p)
 try{$data=New-Object byte[] 32;[void]$stream.Read($data,0,32);if(-not [Text.Encoding]::ASCII.GetString($data).Contains('Standard ACE DB')){throw "Not a genuine Access ACE .accdb: $p"}}
 finally{$stream.Dispose()}
}
function ReadValueList([string]$src){
 # Original GURBELEN-18 value lists use ';' separators; no quoted embedded semicolons.
 $out=New-Object 'System.Collections.Generic.List[string]'
 foreach($piece in ($src -split ';')){
  $v=$piece.Trim().Trim('"').Replace('""','"')
  $out.Add($v)
 }
 return ,$out.ToArray()
}
function Quoted([string]$str){return '"'+$str.Replace('"','""')+'"'}
try{
 if(-not (Test-Path -LiteralPath $Templates)){New-Item -Type Directory -Path $Templates|Out-Null}
 Set-Content -LiteralPath $Audit -Encoding UTF8 -Value 'Lithos clean original-schema template generation'
 if(-not $OriginalPath){
  foreach($candidate in @((Join-Path $Root 'GURBELEN-18.accdb'),(Join-Path $Root 'GURBELEN-18(1).accdb'))){
   if(Test-Path -LiteralPath $candidate){$OriginalPath=$candidate;break}
  }
 }
 if(-not $OriginalPath){
  Add-Type -AssemblyName System.Windows.Forms
  $pick=New-Object System.Windows.Forms.OpenFileDialog
  $pick.Title='Select your original GURBELEN-18.accdb (not modified)'
  $pick.Filter='Access Database (*.accdb)|*.accdb'
  if($pick.ShowDialog() -ne [System.Windows.Forms.DialogResult]::OK){throw 'Original Access database was not selected.'}
  $OriginalPath=$pick.FileName
 }
 $OriginalPath=(Resolve-Path -LiteralPath $OriginalPath).Path
 if($OriginalPath -ieq $TurkishTemplatePath -or $OriginalPath -ieq $EnglishTemplatePath){throw 'Original and output paths must be different'}
 if((Test-Path -LiteralPath $TurkishTemplatePath) -or (Test-Path -LiteralPath $EnglishTemplatePath)){
  throw 'Template output already exists. Move or rename previous template files before a clean build. The script will not overwrite them.'
 }
 ReadAce $OriginalPath
 Log "ORIGINAL (read-only): $OriginalPath"
 $script:Current='connecting to Access DAO'
 try{$dao=New-Object -ComObject 'DAO.DBEngine.120'}
 catch{throw "Access ACE/DAO is not installed for this PowerShell architecture: $($_.Exception.Message)"}
 $script:Current='copying source database'
 Copy-Item -LiteralPath $OriginalPath -Destination $TurkishTemplatePath -ErrorAction Stop
 $createdTR=$true
 $script:Current='emptying original four inventory tables'
 $db=$dao.OpenDatabase($TurkishTemplatePath)
 $targets=@('ÖZELLİKLER','ÇEKİRDEKLER','MAKROLİTLER','MİKROLİT')
 $allNames=@()
 for($i=0;$i -lt [int]$db.TableDefs.Count;$i++){
  $td=$db.TableDefs.Item($i)
  if($td.Name -notlike 'MSys*' -and $td.Name -notlike '~*' -and -not $td.Connect){$allNames+= [string]$td.Name}
 }
 foreach($name in $targets){if($allNames -cnotcontains $name){throw "Original required table not found: $name"}}
 foreach($name in $allNames){if($targets -cnotcontains $name){Log "PRESERVED AUXILIARY TABLE (not emptied): $name"}}
 $pending=[System.Collections.Generic.List[string]]::new()
 foreach($name in $targets){$pending.Add($name)}
 $ws=$dao.Workspaces.Item(0)
 $ws.BeginTrans();$transaction=$true
 try{
  while($pending.Count -gt 0){
   $progress=0;$err=@{}
   foreach($name in @($pending.ToArray())){
    try{$escaped=$name.Replace(']',']]');$db.Execute("DELETE * FROM [$escaped]",128);[void]$pending.Remove($name);$progress++}
    catch{$err[$name]=$_.Exception.Message}
   }
   if($progress -eq 0){throw ('Cannot empty original tables while preserving relationships: '+(($pending|ForEach-Object {"${_}: $($err[$_])"}) -join '; '))}
  }
  ValidateCount $db
  $ws.CommitTrans();$transaction=$false
 }catch{if($transaction){try{$ws.Rollback()}catch{}};throw}
 $db.Close();$db=$null
 Log 'VERIFIED: Turkish original-schema Access copy has 0 inventory records.'
 $script:Current='preparing English-only lookup value lists'
 $Glossary=Join-Path $Root 'veri_sozlugu\GURBELEN18_lookup_TR_EN.csv'
 $CaptionFile=Join-Path $Root 'veri_sozlugu\GURBELEN18_alan_basliklari_TR_EN.csv'
 $translations=@{}
 foreach($entry in (Import-Csv -LiteralPath $Glossary -Encoding UTF8)){
  $key="$($entry.Table)|$($entry.Field)|$($entry.Turkish)"
  if($translations.ContainsKey($key) -and $translations[$key] -cne $entry.English){throw "Conflicting glossary entry: $key"}
  $translations[$key]=[string]$entry.English
 }
 $captions=@{}
 $extraCaptions=@{
  'alinan_urun_sayisi'='Number of Removed Products';'donem'='Period';
  'tasimalik'='Blank Type';'genislik'='Width';'aciklama'='Description';
  'cizim'='Drawing';'patina'='Patina'
 }
 foreach($entry in (Import-Csv -LiteralPath $CaptionFile -Encoding UTF8)){
  $captions["$($entry.Table)|$($entry.Field)"]=[string]$entry.EnglishCaption
 }
 # Preflight on the blank Turkish copy; no partial English copy if a value is missing.
 $db=$dao.OpenDatabase($TurkishTemplatePath,$false,$true)
 $changes=@();$missing=@()
 foreach($name in $targets){
  $table=$db.TableDefs.Item($name)
  for($j=0;$j -lt [int]$table.Fields.Count;$j++){
   $f=$table.Fields.Item($j);$field=[string]$f.Name
   $rowSource=PropertyValue $f 'RowSource'
   $typ=PropertyValue $f 'RowSourceType'
   if([string]::IsNullOrWhiteSpace($rowSource)){continue}
   if($typ -ne 'Value List' -and $typ -ne 'Değer Listesi' -and $typ -ne 'Deger Listesi'){
    $missing+="Unsupported lookup type: $name.$field ($typ)";continue
   }
   $values=ReadValueList $rowSource
   $newValues=@()
   foreach($turkishLookupChoice in $values){
    if($turkishLookupChoice -eq ''){$newValues+= (Quoted '');continue}
    $key="$name|$field|$turkishLookupChoice"
    if(-not $translations.ContainsKey($key)){$missing+="Missing English: $key";continue}
    $newValues+= (Quoted $translations[$key])
   }
   if($newValues.Count -gt 0){
    $newRowSource=($newValues -join ';')
    if($newRowSource.Length -gt 255){$missing+="English lookup list over 255 chars: $name.$field ($($newRowSource.Length))"}
    else{$changes+= [pscustomobject]@{Table=$name;Field=$field;Value=$newRowSource}}
   }
  }
 }
 $db.Close();$db=$null
 if($missing.Count){
  foreach($m in $missing){Log "ERROR: $m"}
  throw "$($missing.Count) lookup translations or structural checks failed (see ACCESS_SABLON_LOG.txt)"
 }
 Log "PREFLIGHT: $($changes.Count) lookup fields translated; no two-column DAO properties are created."
 $script:Current='copying and localizing English template'
 # Safety: fail clearly if a template path ever becomes a dropdown value.
 if(-not (Test-Path -LiteralPath $TurkishTemplatePath -PathType Leaf)){throw "Internal error: Turkish template copy missing at '$TurkishTemplatePath'"}
 if([IO.Path]::GetExtension($TurkishTemplatePath) -ine '.accdb'){throw "Internal error: invalid Turkish template filename '$TurkishTemplatePath'"}
 Copy-Item -LiteralPath $TurkishTemplatePath -Destination $EnglishTemplatePath -ErrorAction Stop
 $createdEN=$true
 $db=$dao.OpenDatabase($EnglishTemplatePath)
 foreach($item in $changes){
  $script:Current="$($item.Table).$($item.Field) RowSource"
  $f=$db.TableDefs.Item($item.Table).Fields.Item($item.Field)
  # Existing native one-column Value List property is updated in place;
  # no RowSource property Append, no BoundColumn/ColumnCount duplication.
  $f.Properties.Item('RowSource').Value=[string]$item.Value
 }
 foreach($name in $targets){
  $t=$db.TableDefs.Item($name)
  for($j=0;$j -lt [int]$t.Fields.Count;$j++){
   $f=$t.Fields.Item($j)
   $key="$name|$($f.Name)"
   $caption=if($captions.ContainsKey($key)){$captions[$key]}else{$null}
   if(-not $caption){
    $compact=([string]$f.Name).ToLowerInvariant().Replace('ı','i').Replace('İ','i').Replace(' ','_')
    if($extraCaptions.ContainsKey($compact)){$caption=$extraCaptions[$compact]}
   }
   if(-not $caption){throw "Missing English field caption (no silent untranslated field): $key"}
   $script:Current="$key English Caption"
   SetCaption $f $caption
  }
 }
 # Rename actual table objects only AFTER all lookup/caption updates.
 # DAO Field.Name is READ-ONLY after a field has been appended, therefore
 # original technical field identifiers are intentionally preserved;
 # English captions become the visible datasheet column headings.
 foreach($name in $targets){
   $script:Current="renaming table $name"
   $targetTable=$db.TableDefs.Item($name)
   $targetTable.Name=[string]$EnglishTableNames[$name]
 }
 ValidateCount $db $true
 $db.Close();$db=$null
 $script:Current='reopening and verifying English template'
 $db=$dao.OpenDatabase($EnglishTemplatePath,$false,$true)
 foreach($item in $changes){
  $actual=[string]$db.TableDefs.Item($EnglishTableNames[$item.Table]).Fields.Item($item.Field).Properties.Item('RowSource').Value
  if($actual -cne $item.Value){throw "English lookup verification failed: $($item.Table).$($item.Field)"}
 }
 ValidateCount $db $true
 $db.Close();$db=$null
 ReadAce $TurkishTemplatePath;ReadAce $EnglishTemplatePath
 Log 'SUCCESS: two empty .accdb templates. EN physical table names are English; original technical field names are preserved with English Caption properties.'
 Log "TR: $TurkishTemplatePath"
 Log "EN: $EnglishTemplatePath"
 Log 'EN lookup values are stored in English; original Turkish source database remains untouched.'
 Log 'Unresolved abbreviations ADÇ and SB remain unchanged; review their scientific meanings.'
 exit 0
}catch{
 Write-Host "FAILED at $($script:Current): $($_.Exception.Message)" -ForegroundColor Red
 Write-Host "DETAIL: $($_.ScriptStackTrace)" -ForegroundColor DarkYellow
 if(Test-Path -LiteralPath $Audit){Add-Content -LiteralPath $Audit -Encoding UTF8 -Value "FAILED at $($script:Current): $($_.Exception.Message)`nDETAIL: $($_.ScriptStackTrace)"}
 if($db){try{$db.Close()}catch{}}
 if($createdEN -and (Test-Path -LiteralPath $EnglishTemplatePath)){try{Remove-Item -LiteralPath $EnglishTemplatePath -Force}catch{}}
 if($createdTR -and (Test-Path -LiteralPath $TurkishTemplatePath)){try{Remove-Item -LiteralPath $TurkishTemplatePath -Force}catch{}}
 exit 1
}
