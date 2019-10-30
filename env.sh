#!/bin/bash
_taskgraph_complete() {
    local tasks cur
    tasks=$(ls -d tasks/* | sed 's/.*\///')

    cur="${COMP_WORDS[COMP_CWORD]}"

    COMPREPLY=( $(compgen -W "$tasks" -- ${cur}) )
    return 0
}

#taken from https://stackoverflow.com/a/246128
TASKGRAPH_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

PATH=$TASKGRAPH_DIR:$PATH
for exec in $(find taskgraph -executable -type f)
do
    complete -F _taskgraph_complete $(basename $exec)
done