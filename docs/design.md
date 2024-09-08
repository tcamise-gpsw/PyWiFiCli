# Design Documentation

- follow somewhat clean architecture
- main goal is aysnc. Maybe provide sync wrapper.

```mermaid
classDiagram
    direction TB
    namespace Domain {
        class Connection {
            + ssid
            + password
        }
        class ScanResult {
            + ssid
            + rssi
        }
        class ConnectionState {
            Disconnected
            Connecting
            Connected
        }
        class SystemLanguage {
            English
            C
            German
        }
        class DriverType {
            LinuxNMCLI
            LinuxNMCLILegacy
            LinuxWPA
            MacOS
            Windows
        }
        class ScanState {
            Idle
            Scanning
        }
        class IWifiDriver{
            <<interface>>
            + SystemLanguage
            + DriverType
            + tuple~ConnectionState, str~ connection_state*
            + ScanState scan_state*
            + str current_interface*
            + set~str~ available_interfaces
            + bool is_enabled*
            + scan() set~ScanResult~*
            + connect(Connection) bool*
            + disconnect(Connection) bool*
            + set_interface(str) bool*
            + enable(bool) bool*
        }
    }
    namespace Implementation {
        class WifiDriverFactory {
            Detects SystemLanguage and Operating System
            to choose suitable driver.
            + str sudo_password
            + getDriver() IWifiDriver
        }
    }
    WifiDriverFactory --> IWifiDriver
```

We're currently only supporting english. Given the above simple architecture, any additional languages will need to
completely reimplement an `IWifiDriver` for each OS. Once / if more languages are supported it might make sense to
create per-OS interfaces such that the different languages only need to implement a few hooks.