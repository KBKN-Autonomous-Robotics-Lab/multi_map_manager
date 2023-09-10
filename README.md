# multi_map_manager
This repository supports large-scale waypoint navigation by switching between multiple environmental maps.

## Dependency Repositories
- https://github.com/KBKN-Autonomous-Robotics-Lab/orange_navigation.git

## Setup
1. Complete the above repository setup.
2. Register to alias to use the python interpreter in the virtual environment (venv) created during the setup above.
```
$ echo "export VENV_PYTHON=path/to/orange_navigation/waypoint_manager/venv/bin/python3" >> ~/.bashrc
$ source ~/.bashrc
$ echo "alias map_merger='$VENV_PYTHON path/to/map_merger/map_merger.py'" >> ~/.bashrc
$ echo "alias map_trimmer='$VENV_PYTHON path/to/multi_map_manager/map_merger/map_trimmer.py'" >> ~/.bashrc
```
