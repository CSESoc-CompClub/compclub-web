# Randomly generate a secret key. ONLY USE THIS FOR DEVELOPMENT!

# Copied from http://dbadailystuff.com/2013/03/11/get-hash-a-powershell-hash-function
function Get-Hash
{
    Param
    (
        [parameter(Mandatory=$true, ValueFromPipeline=$true, ParameterSetName="set1")]
        [String]
        $text,
        [parameter(Position=0, Mandatory=$true, 
        ValueFromPipeline=$false, ParameterSetName="set2")]
        [String]
        $file = "",
        [parameter(Mandatory=$false, ValueFromPipeline=$false)]
        [ValidateSet("MD5", "SHA", "SHA1", "SHA-256", "SHA-384", "SHA-512")]
        [String]
        $algorithm = "SHA1"
    )
    Begin
    {
        $hashAlgorithm = [System.Security.Cryptography.HashAlgorithm]::Create($algorithm)
    }
    Process
    {
        $md5StringBuilder = New-Object System.Text.StringBuilder 50
        $ue = New-Object System.Text.UTF8Encoding

        if ($file){
            try {
                if (!(Test-Path -literalpath $file)){
                    throw "Test-Path returned false."
                }
            }
            catch {
                throw "Get-Hash - File not found or without permisions: [$file]. $_"
            }
            try {
                [System.IO.FileStream]$fileStream = [System.IO.File]::Open($file, [System.IO.FileMode]::Open);
                $hashAlgorithm.ComputeHash($fileStream) | 
                    % { [void] $md5StringBuilder.Append($_.ToString("x2")) }
            }
            catch {
                throw "Get-Hash - Error reading or hashing the file: [$file]"
            }
            finally {
                $fileStream.Close()
                $fileStream.Dispose()
            }
        }
        else {
            $hashAlgorithm.ComputeHash($ue.GetBytes($text)) | 
                % { [void] $md5StringBuilder.Append($_.ToString("x2")) }
        }

        return $md5StringBuilder.ToString()
    }
}

$env:SECRET_KEY = Get-Date | Get-Hash