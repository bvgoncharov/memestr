#!/usr/bin/env bash

for i in {20000..20029}
do
    for j in {0..7}
    do
        bash production_IMR_non_mem_rec_submit.sh ${i}_dynesty ${j}
    done
done
