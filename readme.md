# JACINTA

**J**oint **A**utonomous **C**oding, **I**nference, and **N**otary **T**ask **A**gent

Co-created by ChatGPT 4o Mini

Progress notes summarised in ./progress

# Running the agent

## Installation

`./install.sh`

## Background Runtime

`./run.sh`

## CLI

### Make sure the cli.py file is executable:
`chmod +x src/cli.py`

### List tasks:
`./src/cli.py list completed`
`./src/cli.py list current`
`./src/cli.py list pending`

### Create a new task:
`./src/cli.py new`

### Cancel a task (replace <task_id> with the actual task ID):
`./src/cli.py cancel <task_id>`
