# Currency Exchange

**Currency Exchange** is an application for working with currency exchange rates. It provides functionality for retrieving current exchange rates, converting currencies, and managing a database.

---

## Table of Contents

- [Description](#description)
- [Requirements](#requirements)
- [Installation](#installation)
- [Scripts](#scripts)
- [Running the Application](#running-the-application)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Notes](#notes)

---

## Description

The **Currency Exchange** application is designed to automate currency-related tasks. Key features include:
- Retrieving current exchange rates via API.
- Currency conversion.
- Managing a database to store exchange rate information.
- Support for modular testing.

---

## Requirements

Before starting, ensure you have the following components installed:

- **Git** for repository management.
- Internet access for dependency installation.

> **Note:** Python and dependencies will be automatically installed using [Rye](https://rye-up.com/).

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Dimkin33/Currency_Exchange.git
   cd Currency_Exchange
   ```

2. Ensure the `.env` file exists in the root directory. If it does not, create it based on the `.env.example` file.

3. Run the main script:
   ```bash
   bash script/start.sh
   ```

The script will automatically:
- Check for the `.env` file.
- Install [Rye](https://rye-up.com/) if it is not already installed.
- Update the repository to the latest version of the `main` branch.
- Install dependencies.
- Initialize the database.
- Start the server.

---

## Scripts

The `script/` directory contains the following scripts:

### `start.sh`

The main script for starting the project. It performs the following steps:
1. Checks for the `.env` file.
2. Installs `rye` if it is not already installed.
3. Updates the repository to the latest version of the `main` branch.
4. Installs dependencies using `rye`.
5. Initializes the database.
6. Starts the server.

### `start_background.sh`

Starts the server in the background. Logs are written to the `app.log` file.

### `build.sh`

A script for building the project. It performs:
- Repository update.
- Dependency installation.
- Project build using `rye build`.

### `test.sh`

A script for running tests. It performs:
- Dependency installation.
- Test execution using `rye run test`.

---

## Running the Application

To run the application, execute the following command:

```bash
bash script/start.sh
```

To run the application in the background, use:

```bash
bash script/start_background.sh
```

---

## Testing

To run tests, execute:

```bash
bash script/test.sh
```

---

## Project Structure

- `src/` — Application source code.
- `tests/` — Unit tests.
- `script/` — Auxiliary scripts.
- `.env` and `.env.example` — Environment configuration files.
- `pyproject.toml` — Project configuration, including dependencies and commands.

---

## Notes

- Ensure you have access to the `main` branch in the remote repository.
- Server logs are displayed in the console. To write logs to a file, use background execution.
- If the script fails, check the log output for diagnostics.