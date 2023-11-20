# odrive-can


**PRE-RELEASE, WORK IN PROGRESS**


---

[**Documentation**](https://roxautomation.gitlab.io/components/odrive-can)


---

Use odrive motion controller with CAN inteface


## CLI interface

    Usage: odrive_can [OPTIONS] COMMAND [ARGS]...

    Options:
    --help  Show this message and exit.

    Commands:
    info     Print package info
    inspect  Inspect and decode ODrive CAN messages
    mock     Mock ODrive CAN interface


## Quick start

1. create a virtual can adapter (see [docs](https://odrive-can-roxautomation-components-9f5f4b809336bc0ecbd5b8cd8e4.gitlab.io/can_tools/#virtual-can))
2. in first terminal run `odrive_can mock`
3. in second terminal run `odrive_can inspect`

## Development



### Virtual environment

create virtual envrionment with   `make venv`

### Devcontainer

* `docker` folder contains devcontainer environment.
* `.devcontainer` is VSCode devcontainer environment


**note**: the container needs to be restarted each time device is reconnected.
