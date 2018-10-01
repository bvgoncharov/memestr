#!/usr/bin/env bash

source setup_default.sh ${0}

sbatch ${JOB_NAME} ${OUTPUT} ${TIME} ${NTASKS} ${MEM_PER_CPU} ${CPUS_PER_TASK} ${EMAIL}<<EOF
#!/usr/bin/env bash
JOB=run_basic_job.py
SCRIPT=run_basic_injection_nrsur
INJECTION_MODEL=time_domain_nr_sur_waveform_with_memory
RECOVERY_MODEL=time_domain_nr_sur_waveform_without_memory
srun python \${JOB} ${OUTDIR} \${SCRIPT} \${INJECTION_MODEL} \${RECOVERY_MODEL} $@
EOF