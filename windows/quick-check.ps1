[CmdletBinding()]
param(
    [string]$OutputPath = (Join-Path (Get-Location) 'laptop-report.json')
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-SafeValue {
    param(
        [scriptblock]$Getter,
        [object]$Fallback = $null
    )

    try {
        $value = & $Getter
        if ($null -eq $value -or [string]::IsNullOrWhiteSpace([string]$value)) {
            return $Fallback
        }
        return $value
    } catch {
        return $Fallback
    }
}

function Get-CapacityGb {
    param([object]$Bytes)
    if ($null -eq $Bytes) { return $null }
    return [math]::Round(([double]$Bytes / 1GB), 1)
}

function Get-BatteryData {
    $battery = Get-CimInstance -ClassName Win32_Battery -ErrorAction SilentlyContinue | Select-Object -First 1
    $designCapacity = Get-SafeValue { (Get-CimInstance -Namespace 'root\wmi' -ClassName BatteryStaticData -ErrorAction Stop | Select-Object -First 1).DesignedCapacity }
    $fullChargeCapacity = Get-SafeValue { (Get-CimInstance -Namespace 'root\wmi' -ClassName BatteryFullChargedCapacity -ErrorAction Stop | Select-Object -First 1).FullChargedCapacity }
    $health = $null
    if ($designCapacity -and $fullChargeCapacity -and [double]$designCapacity -gt 0) {
        $health = [math]::Round(([double]$fullChargeCapacity / [double]$designCapacity) * 100, 1)
    }

    return [ordered]@{
        status = if ($null -eq $battery) { 'not_available' } else { 'measured' }
        design_capacity_mwh = $designCapacity
        full_charge_capacity_mwh = $fullChargeCapacity
        health_percent = $health
        charge_percent = if ($battery) { $battery.EstimatedChargeRemaining } else { $null }
        battery_status = if ($battery) { $battery.Status } else { $null }
        cycle_count = Get-SafeValue { (Get-CimInstance -Namespace 'root\wmi' -ClassName BatteryCycleCount -ErrorAction Stop | Select-Object -First 1).CycleCount }
        temperature_c = $null
        limitations = @('Windows hardware support varies by manufacturer; unavailable fields are left blank.')
    }
}

function Get-MemoryData {
    $modules = @(Get-CimInstance Win32_PhysicalMemory -ErrorAction SilentlyContinue)
    $totalBytes = ($modules | Measure-Object -Property Capacity -Sum).Sum
    $computer = Get-CimInstance Win32_ComputerSystem -ErrorAction SilentlyContinue
    $availableBytes = if ($computer) { $computer.TotalPhysicalMemory - (Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory * 1KB } else { $null }

    return [ordered]@{
        total_gb = Get-CapacityGb $totalBytes
        available_gb = Get-CapacityGb $availableBytes
        module_count = $modules.Count
        slots_occupied = $modules.Count
        speed_mhz = if ($modules.Count -gt 0) { @($modules | Select-Object -ExpandProperty Speed -Unique) } else { @() }
        types = if ($modules.Count -gt 0) { @($modules | Select-Object -ExpandProperty SMBIOSMemoryType -Unique) } else { @() }
        channel_mode = 'not_available'
        upgradeability = 'requires physical confirmation'
    }
}

function Get-StorageData {
    $drives = @(Get-CimInstance Win32_DiskDrive -ErrorAction SilentlyContinue)
    return @($drives | ForEach-Object {
        $driveType = if ($_.Model -match 'NVMe|MZVLB|MZVL') { 'NVMe SSD' } elseif ($_.MediaType -match 'SSD') { 'SSD' } elseif ($_.MediaType -match 'Hard') { 'HDD' } else { 'Unknown' }
        [ordered]@{
            model = $_.Model
            drive_type = $driveType
            media_type = $_.MediaType
            interface = $_.InterfaceType
            capacity_gb = Get-CapacityGb $_.Size
            serial = $_.SerialNumber
            smart_status = Get-SafeValue { (Get-CimInstance -Namespace 'root\wmi' -ClassName MSStorageDriver_FailurePredictStatus -ErrorAction Stop | Where-Object InstanceName -Like "*$($_.PNPDeviceID)*" | Select-Object -First 1).PredictFailure }
            temperature_c = $null
            limitations = @('Detailed NVMe/SATA SMART attributes require vendor or administrator support.')
        }
    })
}

function Get-SystemData {
    $computer = Get-CimInstance Win32_ComputerSystem
    $os = Get-CimInstance Win32_OperatingSystem
    $cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
    $gpus = @(Get-CimInstance Win32_VideoController -ErrorAction SilentlyContinue)

    return [ordered]@{
        manufacturer = $computer.Manufacturer
        model = $computer.Model
        operating_system = $os.Caption
        os_version = $os.Version
        cpu = [ordered]@{
            name = $cpu.Name
            cores = $cpu.NumberOfCores
            threads = $cpu.NumberOfLogicalProcessors
            max_clock_mhz = $cpu.MaxClockSpeed
        }
        gpus = @($gpus | ForEach-Object {
            [ordered]@{
                name = $_.Name
                adapter_ram_gb = Get-CapacityGb $_.AdapterRAM
                driver_version = $_.DriverVersion
            }
        })
    }
}

$report = [ordered]@{
    schema_version = '1.0'
    generated_at = (Get-Date).ToUniversalTime().ToString('o')
    checker = [ordered]@{ name = 'LaptopAudit'; mode = 'quick-check'; platform = 'Windows' }
    device = Get-SystemData
    battery = Get-BatteryData
    memory = Get-MemoryData
    storage = Get-StorageData
    thermals = [ordered]@{ status = 'not_tested'; idle_temperature_c = $null; load_temperature_c = $null; throttling = 'not_tested' }
    physical_inspection = [ordered]@{ status = 'not_tested'; items = @() }
}

$parent = Split-Path -Parent $OutputPath
if ($parent -and -not (Test-Path $parent)) {
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
}
$report | ConvertTo-Json -Depth 8 | Set-Content -Path $OutputPath -Encoding UTF8
Write-Output "Report written to $OutputPath"
