#!/usr/bin/env bash

#bash production_IMR_time_phase_submit.sh 0_dynesty

input="n_effs_additional_runs"
i=0
while IFS= read -r line
do
  if [[ ${line} -gt "0" ]]
  then
    for ((j=0; j<=${line}; j++)); do
      bash production_IMR_non_mem_rec_submit.sh ${i}_dynesty ${j}
    done
  fi
  ((i++))
done < "$input"
