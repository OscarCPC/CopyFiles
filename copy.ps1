#Validacion de parametros de parametros. 
param(
    [Parameter(mandatory=$true)]
    [string]$fich
)

#Función de copia de ficheros.
function getFiles($fich){
    #Contadores
    $success  = 0    
    $fail = 0
    #Creación de archivo de log.
	if ((Test-Path ".\log.txt") -eq $false) {
		New-Item -Path ".\log.txt" -ItemType "file"
	}
    foreach ($line in (Get-Content $fich)){
        Copy-Item -Path $line -Destination ".\output" -Verbose
        #validación de ejecución correcta del comando de copia
        if($? -eq $true){
            $success++
        } else {            
            Add-Content .\log.txt "`n$line"
            $fail++
        }       
        
    }
	Write-Host "Copiados $success archivos correctamente"
	if ($fail -gt 0) {
		Write-Host "$fail archivos falllidos. Revisar log.txt"
	}
}

#Validaciones.
if ((Test-Path $fich) -eq $true){
   if ((Test-Path ".\output") -eq $true){
       getFiles($fich)
   } else {        
        New-Item -Path '.\output' -ItemType Directory
        getFiles($fich)
   }
} else {
    Write-Host "Falta archivo o el archivo no es valido."
}  
