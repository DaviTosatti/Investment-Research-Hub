[CmdletBinding()]
param(
    [ValidateSet('Start', 'Stop', 'Check', 'Setup')]
    [string] $Action = 'Start',
    [string] $RuntimeRoot = '',
    [string] $DataRoot = '',
    [switch] $NoBrowser,
    [switch] $NonInteractive
)

# ASCII source for Windows PowerShell 5.1. Paths and arguments remain Unicode.
Set-StrictMode -Version 2.0
$ErrorActionPreference = 'Stop'
$script:PythonVersion = '3.12.14'
$script:VcDlls = @(
    'vcruntime140.dll', 'vcruntime140_1.dll', 'msvcp140.dll',
    'msvcp140_1.dll', 'msvcp140_2.dll', 'msvcp140_atomic_wait.dll',
    'msvcp140_codecvt_ids.dll', 'concrt140.dll'
)

function Assert-WindowsHost {
    if ($PSVersionTable.PSVersion -lt [version] '5.1') {
        throw 'Use o Windows PowerShell 5.1 ou superior.'
    }
    if ([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT -or
        [Environment]::OSVersion.Version.Major -lt 10) {
        throw 'Este bootstrap requer Windows 10/11 x64 nativo.'
    }
    $nativeArchitecture = [Microsoft.Win32.Registry]::GetValue(
        'HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\Environment',
        'PROCESSOR_ARCHITECTURE', ''
    )
    if (-not [Environment]::Is64BitProcess -or
        -not [Environment]::Is64BitOperatingSystem -or $nativeArchitecture -ne 'AMD64') {
        throw 'Use Windows x64 e PowerShell de 64 bits. Abra um dos arquivos Hub.cmd.'
    }
}

function Get-FullDirectory([string] $Path) {
    if ([string]::IsNullOrWhiteSpace($Path)) { throw 'O caminho nao pode estar vazio.' }
    $full = [IO.Path]::GetFullPath($Path)
    $volume = [IO.Path]::GetPathRoot($full)
    if ($full -ne $volume) { $full = $full.TrimEnd([char[]] '\/') }
    return $full
}

function Get-RequiredFiles([string] $Name) {
    switch ($Name) {
        'uv' { return @('uv.exe') }
        'node' { return @('node.exe', 'npm.cmd', 'node_modules\npm\bin\npm-cli.js') }
        'vclibs' { return $script:VcDlls }
        'postgres' {
            return @(
                'bin\pg_ctl.exe', 'bin\postgres.exe', 'bin\initdb.exe',
                'bin\pg_isready.exe', 'bin\psql.exe', 'bin\createdb.exe',
                'share\postgresql.conf.sample'
            ) + @($script:VcDlls | ForEach-Object { 'bin\' + $_ })
        }
    }
    throw 'Ferramenta desconhecida.'
}

function Test-ToolFiles([string] $Directory, [string] $Name, [string] $Version) {
    foreach ($relative in (Get-RequiredFiles $Name)) {
        if (-not (Test-Path -LiteralPath (Join-Path $Directory $relative) -PathType Leaf)) {
            return $false
        }
    }
    if ($Name -eq 'vclibs') { return $true }
    $executable = switch ($Name) {
        'uv' { 'uv.exe' }
        'node' { 'node.exe' }
        'postgres' { 'bin\pg_ctl.exe' }
    }
    $savedPreference = $ErrorActionPreference
    try {
        # PS 5.1 treats redirected native stderr as ErrorRecords, even on success.
        $ErrorActionPreference = 'Continue'
        $global:LASTEXITCODE = $null
        $output = & (Join-Path $Directory $executable) --version 2>&1
        $code = $global:LASTEXITCODE
    }
    catch { return $false }
    finally { $ErrorActionPreference = $savedPreference }
    if ($null -eq $code -or $code -ne 0) { return $false }
    $actual = ($output | ForEach-Object { [string] $_ }) -join "`n"
    $escaped = [regex]::Escape($Version)
    switch ($Name) {
        'uv' { return $actual -match ('^uv ' + $escaped + '(\s|$)') }
        'node' { return $actual.Trim() -ceq ('v' + $Version) }
        'postgres' {
            $pgVersion = [regex]::Escape(($Version -split '-')[0])
            return $actual.Trim() -match ('^pg_ctl \(PostgreSQL\) ' + $pgVersion + '$')
        }
    }
}

function Read-Downloads([string] $Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw 'Falta scripts\windows\downloads.json. Extraia a distribuicao completa do Hub.'
    }
    try { $manifest = Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-Json }
    catch { throw 'downloads.json invalido. Restaure o manifesto oficial do Hub.' }
    if ($null -eq $manifest -or $null -eq $manifest.PSObject.Properties['schema_version'] -or
        ($manifest.schema_version -isnot [int] -and $manifest.schema_version -isnot [long]) -or
        $manifest.schema_version -ne 1 -or
        $null -eq $manifest.PSObject.Properties['python_version'] -or
        $manifest.python_version -cne $script:PythonVersion -or
        $null -eq $manifest.PSObject.Properties['downloads']) {
        throw 'Manifesto incompativel: requer schema_version 1 e Python 3.12.14.'
    }
    $items = @{}
    foreach ($name in @('uv', 'node', 'vclibs', 'postgres')) {
        if ($null -eq $manifest.downloads -or
            $null -eq $manifest.downloads.PSObject.Properties[$name]) {
            throw "Falta downloads.$name no manifesto oficial."
        }
        $item = $manifest.downloads.$name
        foreach ($field in @('version', 'url', 'sha256', 'archive_root')) {
            if ($null -eq $item -or $null -eq $item.PSObject.Properties[$field] -or
                $item.$field -isnot [string]) {
                throw "Campo invalido em downloads.${name}: $field."
            }
        }
        if ($item.version -cnotmatch '^\d+(\.\d+){1,3}(-\d+)?$' -or
            $item.sha256 -cnotmatch '^[a-fA-F0-9]{64}$') {
            throw "Versao ou SHA256 invalido em downloads.$name."
        }
        $uri = $null
        if (-not [Uri]::TryCreate($item.url, [UriKind]::Absolute, [ref] $uri) -or
            $uri.Scheme -ne 'https' -or $uri.Port -ne 443 -or $uri.UserInfo -ne '' -or
            $uri.Query -ne '' -or $uri.Fragment -ne '') {
            throw "downloads.$name requer URL HTTPS oficial sem credenciais."
        }
        $version = [regex]::Escape($item.version)
        $official = switch ($name) {
            'uv' {
                $uri.Host -eq 'github.com' -and $uri.AbsolutePath -cmatch (
                    '^/astral-sh/uv/releases/download/' + $version + '/uv-x86_64-pc-windows-msvc\.zip$'
                ) -and $item.archive_root -ceq ''
            }
            'node' {
                $uri.Host -eq 'nodejs.org' -and $uri.AbsolutePath -cmatch (
                    '^/dist/v' + $version + '/node-v' + $version + '-win-x64\.zip$'
                ) -and $item.archive_root -ceq ('node-v' + $item.version + '-win-x64')
            }
            'vclibs' {
                $uri.Host -eq 'download.microsoft.com' -and $uri.AbsolutePath -cmatch (
                    '^/download/[a-zA-Z0-9/-]+/Microsoft\.VCLibs\.x64\.14\.00\.Desktop\.appx$'
                ) -and $item.archive_root -ceq ''
            }
            'postgres' {
                $uri.Host -eq 'get.enterprisedb.com' -and $uri.AbsolutePath -cmatch (
                    '^/postgresql/postgresql-' + $version + '(-\d+)?-windows-x64-binaries\.zip$'
                ) -and $item.archive_root -ceq 'pgsql'
            }
        }
        if (-not $official) { throw "URL ou archive_root nao oficial para downloads.$name." }
        $items[$name] = $item
    }
    return $items
}

function Enter-InstallMutex([string] $Directory) {
    $hasher = [Security.Cryptography.SHA256]::Create()
    try {
        $bytes = [Text.Encoding]::UTF8.GetBytes($Directory.ToUpperInvariant())
        $digest = [BitConverter]::ToString($hasher.ComputeHash($bytes)).Replace('-', '')
    }
    finally { $hasher.Dispose() }
    $mutex = [Threading.Mutex]::new($false, ('Global\InvestmentResearchHub.Install.' + $digest))
    try {
        Write-Host 'Aguardando acesso exclusivo ao ambiente portatil...'
        for ($second = 0; $second -lt 600; $second++) {
            try { $acquired = $mutex.WaitOne(1000) }
            catch [Threading.AbandonedMutexException] { $acquired = $true }
            if ($acquired) { return $mutex }
            if ($second % 30 -eq 29) { Write-Host 'Outra preparacao esta em andamento; aguardando...' }
        }
        throw 'Outra preparacao ainda esta ativa. Aguarde e tente novamente.'
    }
    catch { $mutex.Dispose(); throw }
}

function Get-FileSha256([string] $Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash
}

function Save-HttpsDownload([Uri] $Uri, [string] $Destination, [string] $Name) {
    Add-Type -AssemblyName System.Net.Http
    $handler = [Net.Http.HttpClientHandler]::new()
    $handler.AllowAutoRedirect = $false
    $client = [Net.Http.HttpClient]::new($handler)
    $client.Timeout = [TimeSpan]::FromMinutes(30)
    $cancellation = [Threading.CancellationTokenSource]::new([TimeSpan]::FromMinutes(30))
    $reason = 'Falha de rede, TLS ou gravacao'
    try {
        for ($redirect = 0; $redirect -le 8; $redirect++) {
            $response = $null
            try {
                $response = $client.GetAsync(
                    $Uri, [Net.Http.HttpCompletionOption]::ResponseHeadersRead, $cancellation.Token
                ).GetAwaiter().GetResult()
                $status = [int] $response.StatusCode
                if ($status -in @(301, 302, 303, 307, 308)) {
                    $reason = 'Redirecionamento HTTPS invalido'
                    if ($null -eq $response.Headers.Location) { throw 'Redirecionamento sem destino.' }
                    $next = [Uri]::new($Uri, $response.Headers.Location)
                    $allowedHost = $next.Host -eq $Uri.Host -or (
                        $Name -eq 'uv' -and $next.Host -in @(
                            'github.com', 'release-assets.githubusercontent.com',
                            'objects.githubusercontent.com'
                        )
                    )
                    if ($next.Scheme -ne 'https' -or $next.Port -ne 443 -or
                        $next.UserInfo -ne '' -or -not $allowedHost) {
                        throw 'Redirecionamento HTTPS nao autorizado.'
                    }
                    $Uri = $next
                    $reason = 'Falha de rede, TLS ou gravacao'
                    continue
                }
                if ($status -ne 200) { $reason = "HTTP $status"; throw 'Download recusado.' }
                $inputStream = $null
                $outputStream = $null
                try {
                    $inputStream = $response.Content.ReadAsStreamAsync().GetAwaiter().GetResult()
                    $outputStream = [IO.File]::Open(
                        $Destination, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write,
                        [IO.FileShare]::None
                    )
                    [void] $inputStream.CopyToAsync($outputStream, 81920, $cancellation.Token).GetAwaiter().GetResult()
                }
                finally {
                    if ($null -ne $outputStream) { $outputStream.Dispose() }
                    if ($null -ne $inputStream) { $inputStream.Dispose() }
                }
                return
            }
            finally { if ($null -ne $response) { $response.Dispose() } }
        }
        $reason = 'Limite de redirecionamentos excedido'
        throw 'Download interrompido.'
    }
    catch {
        # Do not log signed redirect URLs, headers, proxy credentials or response bodies.
        throw "Falha no download HTTPS de ${Name}: $reason. Verifique a conexao, o proxy, o espaco livre e as permissoes da pasta; tente novamente."
    }
    finally { $client.Dispose(); $handler.Dispose(); $cancellation.Dispose() }
}

function Get-VerifiedArchive([string] $Name, $Spec, [string] $Directory) {
    [void] [IO.Directory]::CreateDirectory($Directory)
    $archive = Join-Path $Directory ($Name + '-' + $Spec.sha256.ToLowerInvariant() + '.zip')
    if (Test-Path -LiteralPath $archive -PathType Leaf) {
        if ((Get-FileSha256 $archive) -ieq $Spec.sha256) { return $archive }
        Write-Host "Cache corrompido de $Name; baixando novamente."
        Remove-Item -LiteralPath $archive -Force
    }
    $partial = $archive + '.part'
    try {
        if (Test-Path -LiteralPath $partial) { Remove-Item -LiteralPath $partial -Force }
        Write-Host "Baixando $Name $($Spec.version) e verificando SHA256..."
        Save-HttpsDownload ([Uri] $Spec.url) $partial $Name
        if ((Get-FileSha256 $partial) -ine $Spec.sha256) {
            throw "SHA256 divergente para $Name. O arquivo foi rejeitado; restaure o manifesto oficial e tente novamente."
        }
        [IO.File]::Move($partial, $archive)
        return $archive
    }
    finally {
        if (Test-Path -LiteralPath $partial) { Remove-Item -LiteralPath $partial -Force }
    }
}

function Expand-SafeZip([string] $Archive, [string] $Directory, [string] $ArchiveRoot) {
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $zip = [IO.Compression.ZipFile]::OpenRead($Archive)
    try {
        $prefix = (Get-FullDirectory $Directory) + [IO.Path]::DirectorySeparatorChar
        $seen = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
        $plan = [Collections.Generic.List[object]]::new()
        foreach ($entry in $zip.Entries) {
            $name = $entry.FullName.Replace('\', '/')
            $isDirectory = $name.EndsWith('/')
            if ($isDirectory) { $name = $name.Substring(0, $name.Length - 1) }
            if ([string]::IsNullOrEmpty($name) -or $name.StartsWith('/')) {
                throw 'ZIP rejeitado: caminho vazio ou absoluto.'
            }
            $parts = $name.Split([char] '/')
            foreach ($part in $parts) {
                if ($part -eq '' -or $part -eq '.' -or $part -eq '..' -or
                    $part -match '[<>:"|?*\x00-\x1f]' -or $part -match '[. ]$' -or
                    $part -match '^(?i:CON|PRN|AUX|NUL|CONIN\$|CONOUT\$|COM[0-9\u00b9\u00b2\u00b3]|LPT[0-9\u00b9\u00b2\u00b3])([. ]|$)') {
                    throw 'ZIP rejeitado: nome de arquivo inseguro no Windows.'
                }
            }
            if ($ArchiveRoot -ne '' -and $parts[0] -cne $ArchiveRoot) {
                throw 'ZIP rejeitado: estrutura diferente de archive_root.'
            }
            $unixType = ($entry.ExternalAttributes -shr 16) -band 0xF000
            if ($unixType -eq 0xA000 -or ($entry.ExternalAttributes -band 0x400) -ne 0) {
                throw 'ZIP rejeitado: links simbolicos ou pontos de nova analise.'
            }
            $relative = $name.Replace([char] '/', [IO.Path]::DirectorySeparatorChar)
            $target = [IO.Path]::GetFullPath([IO.Path]::Combine($Directory, $relative))
            if (-not $target.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase) -or
                -not $seen.Add($target)) {
                throw 'ZIP rejeitado: caminho externo ou arquivo duplicado.'
            }
            $plan.Add([pscustomobject] @{ Entry = $entry; Target = $target; Directory = $isDirectory })
        }
        # Validate every name before writing any entry; never call ExtractToDirectory.
        foreach ($item in $plan) {
            if ($item.Directory) { [void] [IO.Directory]::CreateDirectory($item.Target); continue }
            [void] [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($item.Target))
            [IO.Compression.ZipFileExtensions]::ExtractToFile($item.Entry, $item.Target, $false)
        }
    }
    finally { $zip.Dispose() }
}

function Copy-AppLocalVcRuntime([string] $Source, [string] $PostgresDirectory) {
    $bin = Join-Path $PostgresDirectory 'bin'
    foreach ($dll in $script:VcDlls) {
        $from = Join-Path $Source $dll
        $to = Join-Path $bin $dll
        if (-not (Test-Path -LiteralPath $from -PathType Leaf)) {
            throw "Pacote VCLibs incompleto: falta $dll."
        }
        if (Test-Path -LiteralPath $to) {
            if ((Get-FileSha256 $from) -ine (Get-FileSha256 $to)) {
                throw "DLL conflitante no pacote PostgreSQL: $dll."
            }
        }
        else { [IO.File]::Copy($from, $to, $false) }
    }
}

function Ensure-PortableTool([string] $Name, $Spec, [string] $Root, [bool] $Install) {
    $destination = Join-Path $Root $Name
    $marker = Join-Path $destination '.hub-install.json'
    if (Test-Path -LiteralPath $destination) {
        $valid = $false
        if (Test-Path -LiteralPath $marker -PathType Leaf) {
            try {
                $stamp = Get-Content -LiteralPath $marker -Raw -Encoding UTF8 | ConvertFrom-Json
                $valid = $stamp.schema_version -eq 1 -and $stamp.name -ceq $Name -and
                    $stamp.version -ceq $Spec.version -and $stamp.sha256 -ieq $Spec.sha256 -and
                    (Test-ToolFiles $destination $Name $Spec.version)
                if ($valid -and $Name -eq 'postgres') {
                    foreach ($dll in $script:VcDlls) {
                        if ((Get-FileSha256 (Join-Path $Root ('vclibs\' + $dll))) -ine
                            (Get-FileSha256 (Join-Path $destination ('bin\' + $dll)))) {
                            $valid = $false
                            break
                        }
                    }
                }
            }
            catch { $valid = $false }
        }
        if ($valid) { Write-Host "$Name $($Spec.version) ja preparado."; return }
        throw "Instalacao de $Name incompleta ou divergente em '$destination'. Ela foi preservada. Renomeie essa pasta ou use outro -RuntimeRoot e execute -Action Setup."
    }
    if (-not $Install) { throw "Falta $Name em '$destination'. Execute -Action Setup primeiro." }
    $archive = Get-VerifiedArchive $Name $Spec (Join-Path $Root 'cache\downloads')
    $staging = Join-Path $Root ('.staging\' + $Name + '-' + [Guid]::NewGuid().ToString('N'))
    [void] [IO.Directory]::CreateDirectory($staging)
    try {
        Expand-SafeZip $archive $staging $Spec.archive_root
        $source = $staging
        if ($Spec.archive_root -ne '') { $source = Join-Path $staging $Spec.archive_root }
        if ($Name -eq 'postgres') { Copy-AppLocalVcRuntime (Join-Path $Root 'vclibs') $source }
        if (-not (Test-ToolFiles $source $Name $Spec.version)) {
            throw "Pacote $Name incompleto ou nao executavel no Windows x64. Nenhuma instalacao existente foi substituida."
        }
        $stamp = [ordered] @{
            schema_version = 1; name = $Name; version = $Spec.version; sha256 = $Spec.sha256
        }
        $stamp | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $source '.hub-install.json') -Encoding ASCII
        # Same-volume directory rename publishes only a fully validated installation.
        [IO.Directory]::Move($source, $destination)
        Write-Host "$Name $($Spec.version) instalado no ambiente portatil."
    }
    finally {
        if (Test-Path -LiteralPath $staging) { Remove-Item -LiteralPath $staging -Recurse -Force }
    }
}

function Invoke-CheckedNative([string] $Executable, [string[]] $Arguments, [string] $Description) {
    if (-not (Test-Path -LiteralPath $Executable -PathType Leaf)) {
        throw "$Description indisponivel: executavel local ausente. Execute -Action Setup."
    }
    $savedPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $global:LASTEXITCODE = $null
        & $Executable @Arguments | Out-Host
        $code = $global:LASTEXITCODE
    }
    finally { $ErrorActionPreference = $savedPreference }
    if ($null -eq $code) { $code = 1 }
    if ($code -ne 0) {
        $failure = [Exception]::new("$Description falhou (codigo $code). Corrija o erro acima e tente novamente.")
        $failure.Data['ExitCode'] = [int] $code
        throw $failure
    }
}

$exitCode = 1
$mutex = $null
$oldLocation = $null
$oldTls = $null
$savedEnvironment = @{}
try {
    Assert-WindowsHost
    $checkout = Get-FullDirectory (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
    foreach ($required in @('pyproject.toml', 'uv.lock', 'apps\web\package-lock.json', 'scripts\windows\runtime.py')) {
        if (-not (Test-Path -LiteralPath (Join-Path $checkout $required) -PathType Leaf)) {
            throw "Repositorio incompleto: falta '$required'. Extraia o ZIP completo antes de executar o Hub."
        }
    }
    if ($RuntimeRoot -eq '' -or $DataRoot -eq '') {
        $localData = [Environment]::GetFolderPath([Environment+SpecialFolder]::LocalApplicationData)
        if ([string]::IsNullOrWhiteSpace($localData)) {
            throw 'LocalAppData indisponivel. Informe -RuntimeRoot e -DataRoot explicitamente.'
        }
        $base = Join-Path $localData 'InvestmentResearchHub'
        if ($RuntimeRoot -eq '') { $RuntimeRoot = Join-Path $base 'runtime' }
        if ($DataRoot -eq '') { $DataRoot = Join-Path $base 'data' }
    }
    $RuntimeRoot = Get-FullDirectory $RuntimeRoot
    $DataRoot = Get-FullDirectory $DataRoot
    $python = Join-Path $checkout '.venv-windows\Scripts\python.exe'
    $oldLocation = Get-Location
    Set-Location -LiteralPath $checkout
    $environment = @{
        UV_PROJECT_ENVIRONMENT = Join-Path $checkout '.venv-windows'
        UV_PYTHON_INSTALL_DIR = Join-Path $RuntimeRoot 'python'
        # uv treats these selectors as mutually exclusive, including inherited values.
        UV_PYTHON_PREFERENCE = $null
        UV_MANAGED_PYTHON = '1'
        UV_CACHE_DIR = Join-Path $RuntimeRoot 'cache\uv'
        PATH = (Join-Path $RuntimeRoot 'node') + [IO.Path]::PathSeparator + $env:PATH
    }
    if ($NonInteractive) { $environment['UV_NO_PROGRESS'] = '1' }
    foreach ($key in $environment.Keys) {
        $savedEnvironment[$key] = [Environment]::GetEnvironmentVariable($key, 'Process')
        [Environment]::SetEnvironmentVariable($key, $environment[$key], 'Process')
    }
    if ($Action -ne 'Stop') {
        $downloads = Read-Downloads (Join-Path $PSScriptRoot 'downloads.json')
        $install = $Action -in @('Start', 'Setup')
        if ($install) { $mutex = Enter-InstallMutex $RuntimeRoot }
        try {
            if ($install) {
                [void] [IO.Directory]::CreateDirectory($RuntimeRoot)
                $oldTls = [Net.ServicePointManager]::SecurityProtocol
                [Net.ServicePointManager]::SecurityProtocol = $oldTls -bor [Net.SecurityProtocolType]::Tls12
            }
            foreach ($name in @('uv', 'node', 'vclibs', 'postgres')) {
                Ensure-PortableTool $name $downloads[$name] $RuntimeRoot $install
            }
            if ($install) {
                $uv = Join-Path $RuntimeRoot 'uv\uv.exe'
                Invoke-CheckedNative $uv @('python', 'install', $script:PythonVersion, '--no-bin', '--no-registry') 'A instalacao do Python'
                Invoke-CheckedNative $uv @('sync', '--locked', '--python', $script:PythonVersion, '--project', $checkout) 'A sincronizacao Python'
            }
        }
        finally {
            if ($null -ne $mutex) { $mutex.ReleaseMutex(); $mutex.Dispose(); $mutex = $null }
        }
    }
    if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
        throw 'Python local ausente em .venv-windows\Scripts\python.exe. Execute -Action Setup primeiro.'
    }
    $runtimeArguments = @(
        (Join-Path $PSScriptRoot 'runtime.py'), $Action.ToLowerInvariant(),
        '--root', $checkout, '--runtime-root', $RuntimeRoot, '--data-root', $DataRoot
    )
    if ($NoBrowser) { $runtimeArguments += '--no-browser' }
    if ($NonInteractive) { $runtimeArguments += '--non-interactive' }
    # Foreground by design: runtime.py owns health checks, browser and stop requests.
    Invoke-CheckedNative $python $runtimeArguments ('O runtime do Hub (' + $Action + ')')
    $exitCode = 0
}
catch {
    if ($_.Exception.Data.Contains('ExitCode')) { $exitCode = [int] $_.Exception.Data['ExitCode'] }
    [Console]::Error.WriteLine('Hub: ' + $_.Exception.Message)
}
finally {
    if ($null -ne $mutex) { $mutex.ReleaseMutex(); $mutex.Dispose() }
    if ($null -ne $oldTls) { [Net.ServicePointManager]::SecurityProtocol = $oldTls }
    foreach ($key in $savedEnvironment.Keys) {
        [Environment]::SetEnvironmentVariable($key, $savedEnvironment[$key], 'Process')
    }
    if ($null -ne $oldLocation) { Set-Location -LiteralPath $oldLocation }
}
exit $exitCode
