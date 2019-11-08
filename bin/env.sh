#!/bin/bash

#taken from https://stackoverflow.com/a/246128
SOURCE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
TASKGRAPH_PATH=$SOURCE_DIR/..

_taskgraph_complete() {
    local cur

    cur="${COMP_WORDS[COMP_CWORD]}"

    if [ "$COMP_CWORD" -eq 1 ]; then
        COMPREPLY=( $(compgen -W "$(taskgraph commands)" -- "$cur") )
    else
        COMPREPLY=( $(compgen -W "$(taskgraph list)" -- ${cur}) )
    fi
    return 0
}

#prevent from expanding wildcard
alias taskgraph='set -f;taskgraph';taskgraph(){ command taskgraph "$@";set +f;}

PATH=$SOURCE_DIR:$PATH
export PYTHONPATH=$TASKGRAPH_PATH:$PYTHONPATH
complete -F _taskgraph_complete taskgraph