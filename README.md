# RiverDataCollector
Downloads daily records of Javorinka river from www.shmu.sk. Store them to train river prediction model.

## Project structure
.
├── README.md
├── config 
├── main.py
├── poetry.lock
├── pyproject.toml
├── requirements.txt
├── src
│   └── river_data_collector
│       ├── app
│       ├── db
│       ├── river_downloader
│       └── scheduler
└── tests

- config: Configuration files (e.g., settings, credentials).
- poetry.lock: Locked dependency versions (managed by Poetry).
- pyproject.toml: Project metadata and dependencies (Poetry configuration).
- requirements.txt: List of dependencies (alternative to Poetry).
- src: Core application source code.
- app: Application logic and orchestration.
- db: Database interaction logic (e.g., Firebase).
- river_downloader: River data collection scripts. Divided into data source services.
- scheduler: Periodic task scheduling.
- tests: Unit and integration test cases.

## how to run it
Project uses poetry for managing project metadata, dependencies, build systems and scripts.