##########################
##
##########################
#END_OF_HELP

HFile="${HOME}/ahost.map"

verbose=0
stag=""

bsel=0

while getopts "hvt:" opt
do
    case $opt in
        v)
            verbose=1
            ;;
        h)
            grep -B 1000 '^#END_OF_HELP' $0|sed -e '$d'
	    exit 0
            ;;
        t)
            stag="$OPTARG"
            ;;
    esac
done
shift $((OPTIND-1))

sterm="$@"

update_counter() {
    # read global ${sline} , constant ${HFile}
    # local var header uc_
    printf "Updating Counter..."
    local uc_cnt=$( grep -v "^#" ${HFile} | grep "${sline}" | awk '{printf $0"\t0";}' |awk '{printf $2;}' )
    local uc_ncnt=$( expr ${uc_cnt} + 1 )
    local uc_lnum=$( grep -n "^${sline}" ${HFile} | awk -F':' '{printf $1;}' )
    
    # Note -i "" only work for Mac OS. in Standard linux, please remove the ""
    sed -i "" "${uc_lnum}s/.*/${sline}"$'\t'"${uc_ncnt}/" ${HFile}
    printf "done.\n"

}

select_by_term() {
    # read and write global array ${harr}
    # local var header sbt_
    local sbt_sterm=$1
    local sbt_sfield=${2:-1}
    local sbt_tmparr=( )

    if [ "${sbt_sterm}" != "" ]
    then
	for sbt_ln in ${harr[*]}
	do
	    sbt_tmp=$( echo "${sbt_ln}" | cut -f ${sbt_sfield} | grep "${sbt_sterm}" )
	    if [ $?  == 0 ]
	    then
		sbt_tmparr+=("${sbt_ln}")
		bsel=1
	    fi
	done
	harr=( ${sbt_tmparr[@]} )
    fi

}

load_all() {
    # overwtie globar arrary ${harr}
    # local var header la_
    harr=( )
    IFS=$'\n' harr=( $(cat ${HFile} | sed -e 's/^[ ]*//' | {
		la_tags=''
		while read la_ln 
		do
		    if [ "${la_ln}" == "" ]
		    then
			la_tags=''
		    else
			la_tmptest=$( expr "${la_ln}" : "^#" )
			if [ ${la_tmptest} != "0" ]
			then
			    la_tags="$( echo ${la_ln} | tr -d '[#]' )"
			else
			    la_host=$( echo "${la_ln}" | cut -f 1 )
			    la_count=$( echo "${la_ln}"$'\t'"0" | cut -f 2 )
			    echo "${la_host}"$'\t'"${la_tags}"$'\t'"${la_count}"
			fi
		    fi
		done 
	    } | sort -t $'\t' -nrk 3,3 
    ) )
}

list_hosts() {
    # read and print global array ${harr}
    # local var header lh_
    lh_lcnt=1
    printf '\e[1;36m%10s\e[0m : \e[1;33m %-60s \e[1;32m %-30s\e[0m\n' "Choice" "Host" "Tag"
    for lh_ln in ${harr[*]}
    do
	lh_host=$( echo ${lh_ln}|cut -f 1)
	lh_tag=$( echo ${lh_ln}|cut -f 2)
	printf '\e[1;36m%10s\e[0m : \e[1;33m %-60s \e[1;32m %-30s\e[0m\n' "${lh_lcnt}" "${lh_host}" "${lh_tag}"
	lh_lcnt=$((lh_lcnt+1))
    done
}


harr=( )
cnt=0
load_all
select_by_term "${sterm}" 1
select_by_term "${stag}" 2
while [ "${#harr[@]}" -gt 1 ] && ( [ "${bsel}" == 0 ] || [ "${verbose}" == 1 ] )
do
    ttl=${#harr[@]}
    list_hosts
    choice=-1
    field=0
    while [ ${choice} -lt 0 ] || [ ${choice} -gt ${ttl} ]
    do
	printf " \e[1;31m>>\e[0m log to which one? [ \e[1;36m1\e[0m - \e[1;36m%s\e[0m ] or Search (\e[1;36mh\e[0m)ost/(\e[1;36mt\e[0m)ag\e[0m or Toggle (\e[1;36mv\e[0m)erbose[${verbose}]: " "${ttl}"
	read  choice
	choice=$( echo ${choice}|tr -d [' '] )
	if [ "${choice}" == "0" ]
	then
	    choice=-1
	elif [ "${choice}" == 'v' ]
	then
	    verbose=$((1-verbose))
	    choice=-1
	elif [ "${choice}" == 'h' ]
	then
            choice=0
	    field=1
	elif [ "${choice}" == 't' ]
	then
	    choice=0
	    field=2
	elif [ "${choice}" == "" ]
	then
	    choice=-1
	    
	elif [ "$( echo ${choice}|tr -d [:digit:] )" != "" ]
	then
	    choice=-1
	fi

    done

    if [ "${choice}" == "0" ]
    then
	ttarr=( "" "Host" "Tag" )
	printf " \e[1;31m>>>>\e[0m Search ${ttarr[${field}]} [verbose=${verbose}] : "
	read isterm
        select_by_term "${isterm}" ${field}	
    else
	harr=( "${harr[$( expr ${choice} - 1 )]}" )
	bsel=1
    fi
done

if [ ${#harr[@]} == 0 ]
then
    printf "Nothing found...\e[6;33mSorry!!\e[0m\n"
else
    if [ ${#harr[@]} -gt 1 ]
    then
	printf "\e[1;35m[Warning]\e[0m Using the first of ${#harr[@]} matches. Consider \e[1;33m-v\e[0m for choices.\n"
    fi
    sline=$(echo "${harr[0]}"|cut -f 1)
    update_counter
    printf "Connecting to \e[1;33m%s\e[0m ...\n" "${sline}" 
    ssh "${sline}"
fi

