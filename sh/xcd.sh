targ=$1

_XCD_HISTORY="${HOME}/.xcd_history"
_HISTORY_COUNT=100

touch "${_XCD_HISTORY}"

if [[ -n "${targ}" ]]
then
    px=$( find ~/ -type d -regex ".*${targ}[^/]*$" |sort )
else
    # px=$( tail "${_XCD_HISTORY}" | sed '1!G;h;$!d' )
    px=$( head ${_XCD_HISTORY} )
fi

llen=$( echo "${px}"|wc -l )
echo "${px}" |nl

read -p 'which? ' lnum

if [[ -n "${lnum}" ]] && [[ "${lnum}" == [0-9]* ]] && [ "${lnum}" -le "${llen}" ] && [ "${lnum}" -ge 1 ]
then
    ch=$( echo "${px}"|tail -n +${lnum}| head -1 )

    if [[ -n "${ch}" ]]
    then
        { echo ${ch}; cat ${_XCD_HISTORY}; } | nl |sort --key=2.1 -b -u | sort -n | cut -c8- |head -"${_HISTORY_COUNT}"> ${_XCD_HISTORY}.writing
#       { echo ${ch}; cat ${_XCD_HISTORY}; } > ${_XCD_HISTORY}.writing
        mv ${_XCD_HISTORY}.writing ${_XCD_HISTORY}

        cd "${ch}"
    fi
fi
