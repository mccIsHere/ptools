pcmd=$1
input=$2
output=$3
tcount=$4

flen=$( cat ${input}| wc -l )

bsize=$(( ${flen}/${tcount}+1 ))

echo "Input Size: "${flen}
echo "Divided as "${bsize}" * "${tcount}

arr=()
for idx in $(seq ${tcount})
do
    bidx=$(( ${bsize}*(${idx}-1)+1 ))
    echo "${idx}: ${bidx} + ${bsize}"
    tail -n +${bidx} ${input} |head -${bsize} | eval ${pcmd} > ${output}.part${idx} 2>${output}.part${idx}.err &
    lpid=$!
    # echo ${lpid}
    arr+=(${lpid})
    # echo ${arr[@]}
done

for pidx in ${arr[@]}
do
    wait ${pidx}
done

if [ -f "${output}" ]
then
    echo "Warning: File ${output} is going to be overwritten." 
    rm ${output}
fi

touch ${output}

for idx in $(seq ${tcount})
do
    cat ${output}.part${idx} >> ${output}
    rm ${output}.part${idx}
done
