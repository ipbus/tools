#!/bin/bash

#------------------------------------------------------------------------------
function pathadd() {
  # Assert that we got enough arguments
  if [[ $# -ne 2 ]]; then
    echo "drop_from_path: needs 2 arguments"
    return 1
  fi
  PATH_NAME=$1
  PATH_VAL=${!1}
  PATH_ADD=$2

  # Add the new path only if it is not already there
  if [[ ":$PATH_VAL:" != *":$PATH_ADD:"* ]]; then
    # Note
    # ${PARAMETER:+WORD}
    #   This form expands to nothing if the parameter is unset or empty. If it
    #   is set, it does not expand to the parameter's value, but to some text
    #   you can specify
    PATH_VAL="$PATH_ADD${PATH_VAL:+":$PATH_VAL"}"

    echo "- $PATH_NAME += $PATH_ADD"

    # use eval to reset the target
    eval "${PATH_NAME}=${PATH_VAL}"
  fi
}
#------------------------------------------------------------------------------

if [ -n "$ZSH_VERSION" ]; then
   # assume Zsh
   SH_SOURCE=${(%):-%x}
elif [ -n "$BASH_VERSION" ]; then
   # assume Bash
   SH_SOURCE=${BASH_SOURCE}
else
   # asume something else
   echo "Error: only bash and zsh supported"
fi

IPBUSTOOLS_ROOT=$(cd $(dirname ${SH_SOURCE}) && pwd)

export PATH="${IPBUSTOOLS_ROOT}/scripts${PATH:+:}${PATH}"


