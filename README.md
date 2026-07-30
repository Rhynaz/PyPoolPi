# PyPoolPi

> Automatic Pool Cover Controller for Raspberry Pi

[![Python: 3.13+](https://img.shields.io/badge/Python-3.13%2B-blue)](https://www.python.org/)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

**PyPoolPi** is an extensible, event-driven pool cover controller built for the Raspberry Pi (or other Linux single-board computers). Designed around a modular finite state machine, it provides automated opening and closing operations, sensor-based end detection, safety timeouts, custom dive sequences, real-time cover state persistence, an interactive web dashboard + API and MQTT integration for smart home automation.

## 🌟 Key Features

- **Extensible State Machine Controller**: Thread-safe finite state machine managing pool cover states (`OPENING`, `CLOSING`, `STOPPED`, `OPENED`, `CLOSED`, etc.) with pluggable extension modules.
- **Custom Dive Sequence**: Configurable multi-stage closing sequence (hanging, diving, surfacing) to prevent cover folding issues during closing operations.
- **Sensor-Based End Detection**: Automatic stop trigger using sensors with overrun delay for precise full-open and full-close positioning.
- **Safety Timeout Protection**: Automatically halts motor movement if configurable max opening or closing durations are exceeded to protect hardware.
- **Hardware Abstraction Layer**: Clean abstraction for different motor and sensor models and hardware/GPIO libraries.
- **Dynamic Hot-Reloading Configuration**: Configuration system with zero-downtime runtime updates and a TOML config file with hot-reload support on changes.
- **Interactive Web UI & REST API**: Built-in web server serving a control dashboard, API endpoints (`/command`, `/status`, `/config`, `/log`), and Server-Sent Events.
- **MQTT Smart Home Integration**: Full MQTT broker integration for remote command execution, status streaming, and live log broadcasting.
- **State Persistence**: Remembers and restores cover state across service restarts using configurable storage targets.
- **Production-Ready Deployment**: Systemd unit configuration with automated installation and version upgrade scripts for Raspberry Pi OS.

## 🚀 Quick Start & Installation

### Development Setup

1. **Clone the repository**:

   ```sh
   git clone https://github.com/Rhynaz/PyPoolPi.git
   cd PyPoolPi
   ```

2. **Create and activate a Python 3.13 virtual environment**:

   ```sh
   python3.13 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:

   ```sh
   python3.13 -m pip install -r requirements.txt
   ```

4. **Run PyPoolPi**:

   ```sh
   python3.13 main.py
   ```

### Production Installation on Raspberry Pi

#### First Time Installation

1. Clone the repository into a versioned folder (e.g., `~/pypoolpi-v1`):

   ```sh
   git clone https://github.com/Rhynaz/PyPoolPi.git ~/pypoolpi-v1
   ```

2. Run the installation script with `sudo`:

   ```sh
   sudo ~/pypoolpi-v1/pypoolpi_install.sh
   ```

_The script installs system APT packages (`python3-gpiozero`, `python3-flask`, `python3-paho-mqtt`, etc.), sets network binding capabilities (`CAP_NET_BIND_SERVICE`), creates a symlink at `~/pypoolpi`, and enables the `pypoolpi.service` systemd unit._

#### Upgrading to a New Version

To deploy a new release without breaking service state:

1. Clone the new version:

   ```sh
   git clone https://github.com/Rhynaz/PyPoolPi.git ~/pypoolpi-v2
   ```

2. Execute the version switch script:

   ```sh
   sudo ~/pypoolpi-v2/pypoolpi_switch.sh
   ```

_This gracefully stops the running service, updates the symlink to the new directory, and restarts `pypoolpi.service`._

## 🌐 Web UI & API

PyPoolPi hosts an HTTP web server (default port `5000`) serving a control dashboard and API endpoints:

| Endpoint         |    Method     | Description                                           |
| :--------------- | :-----------: | :---------------------------------------------------- |
| `/`              |     `GET`     | Interactive web dashboard                             |
| `/command/open`  |    `POST`     | Trigger cover to open                                 |
| `/command/close` |    `POST`     | Trigger cover to close                                |
| `/command/stop`  |    `POST`     | Trigger cover to stop                                 |
| `/status`        |     `GET`     | Returns current cover state (JSON)                    |
| `/config`        | `GET` / `PUT` | Read or update configuration schema dynamically       |
| `/log`           |     `GET`     | View recent in-memory system log output               |
| `/events`        |     `GET`     | Server-Sent Events (SSE) stream for real-time updates |

## 📡 MQTT Integration

When enabled, PyPoolPi connects to an MQTT broker to integrate seamlessly with smart home platforms:

- **Command Topic** (default: `pypoolpi/command`): Listens for `open`, `close`, or `stop` messages and executes the corresponding command.
- **State Topic** (default: `pypoolpi/state`): Publishes updated state names (`OPENED`, `CLOSED`, `OPENING`, `CLOSING`, `STOPPED`, etc.).
- **Log Topic** (default: `pypoolpi/log`): Publishes log records in real time.

## 📦 Dependencies

- **Python**: 3.13+
- **Operating System**: Linux (Raspberry Pi OS, Debian or equivalent)
- **Hardware**: Raspberry Pi (or similar SBC with GPIO pins) or any PC (when using mock hardware).

|   Package   | Purpose                                                     |
| :---------: | :---------------------------------------------------------- |
| `gpiozero`  | GPIO pin abstraction for motor control & sensor inputs      |
|   `Flask`   | Lightweight web application framework for dashboard & API   |
| `waitress`  | Production WSGI HTTP server                                 |
| `paho-mqtt` | Client library for MQTT communication                       |
| `mashumaro` | Serialization & deserialization for configuration           |
|  `tomli_w`  | TOML encoder for Python                                     |
| `watchdog`  | Filesystem event monitoring for hot-reloading configuration |

## 🏗 Repository Structure & Overview

| Path                       | Description                                                                                             |
| :------------------------- | :------------------------------------------------------------------------------------------------------ |
| `config`                   | Dynamic and thread-safe runtime configuration management system                                         |
| `config/parts`             | Config schema implemented as dataclasses                                                                |
| `controller`               | Main cover controller logic connecting hardware, state machine and persistence                          |
| `controller/extensions`    | Modular state machine plugins for advanced behaviors (dive sequence, end detection, safety timeout)     |
| `controller/state_machine` | Extensible state machine engine, state and extension interface contracts                                |
| `core`                     | Interfaces defining controller, hardware and persistence contracts                                      |
| `hardware`                 | Hardware access implementation and factory for instatiating hardware drivers                            |
| `hardware/motor`           | Motor driver implementations supporting different motors and hardware libraries                         |
| `hardware/sensor`          | Driver implementations interacting with different end detection proximity switches                      |
| `persistence`              | Persistence implementations handling all load / store operations.                                       |
| `persistence/targets`      | Storage backends, supporting file-based persistence and mock targets                                    |
| `persistence/config.py`    | Hot-reloading TOML configuration loader and filesystem event monitor                                    |
| `presentation/http`        | Web interface including an interactive dashboard and HTTP API for controlling the pool cover            |
| `presentation/mqtt`        | MQTT interface for triggering commands, getting the cover state and logs                                |
| `utils`                    | Shared utility modules including thread-safe value holders, caller introspection, and background timers |
| `utils/log`                | Custom configuration based logging setup with exclusion filters and in-memory log buffers               |
| `main.py`                  | Main application entry point, handles command-line arguments, dependency wiring, and graceful shutdown  |
| `pypoolpi.service`         | Systemd service unit for running PyPoolPi automatically as a background daemon                          |
| `pypoolpi_install.sh`      | System installer script for installing dependencies, network capabilities, symlinks, and service        |
| `pypoolpi_run.sh`          | Wrapper script executed by systemd to run PyPoolPi unprivileged in the correct working directory        |
| `pypoolpi_switch.sh`       | Version switcher script that updates symlinks and restarts `pypoolpi.service`                           |

## 🔌 Custom Board Pinout

The system supports configurable GPIO pin assignments. Below is the pin mapping for our custom controller board:

| Pin Number |   Function   |
| :--------: | :----------: |
|     17     | Sensor Data  |
|     27     | Motor Relay  |
|     22     | Motor Relay  |
|     5      | Sensor Power |
|     6      | Backup Relay |

## 📜 License

PyPoolPi - Automatic pool cover controller running on a Raspberry Pi<br>
Copyright (C) 2026 Elias\*

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
