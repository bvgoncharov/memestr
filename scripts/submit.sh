#!/usr/bin/env bash

#Distance vs evidence
#bash IMR_mem_inj_mem_rec.sh                 npoints=5000 alpha=0.1 dlogz=0.1 zero_noise=False sampler=dynesty luminosity_distance=$1 ra=0.684 dec=0.672 psi=4.28 distance_marginalization=True label=IMR_mem_inj_mem_rec
#bash IMR_mem_inj_non_mem_rec.sh             npoints=5000 alpha=0.1 dlogz=0.1 zero_noise=False sampler=dynesty luminosity_distance=$1 ra=0.684 dec=0.672 psi=4.28 distance_marginalization=True label=IMR_mem_inj_non_mem_rec

#Population run
#bash IMR_mem_inj_mem_rec.sh                 npoints=2000 maxmcmc=2000 alpha=0.1 distance_marginalization=True sampler=cpnest nthreads=4 duration=16 random_seed=42 sampling_frequency=2048 filename_base=${0} label=IMR_mem_inj_mem_rec
bash IMR_mem_inj_non_mem_rec.sh              outdir_base=${1} filename_base=${1} npoints=10000 alpha=0.1 distance_marginalization=True sampler=cpnest duration=16 random_seed=42 sampling_frequency=2048 label=IMR_mem_inj_non_mem_rec

#bash IMR_non_mem_inj_mem_rec.sh                 npoints=2000 maxmcmc=1200 alpha=0.1 zero_noise=True distance_marginalization=True sampler=cpnest nthreads=4 duration=16 random_seed=42 sampling_frequency=2048 label=IMR_non_mem_inj_mem_rec
#bash IMR_non_mem_inj_non_mem_rec.sh             npoints=2000 maxmcmc=1200 alpha=0.1 zero_noise=True distance_marginalization=True sampler=cpnest nthreads=4 duration=16 random_seed=42 sampling_frequency=2048 label=IMR_non_mem_inj_non_mem_rec
