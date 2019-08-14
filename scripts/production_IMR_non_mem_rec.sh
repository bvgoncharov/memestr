#!/usr/bin/env bash

source production_IMR_non_mem_rec_setup.sh ${0} ${1}

sbatch ${JOB_NAME} ${OUTPUT} ${TIME} ${NTASKS} ${MEM_PER_CPU} ${CPUS_PER_TASK} ${EMAIL} ${ARRAY}<<EOF
#!/usr/bin/env bash
JOB=run_basic_job.py
SCRIPT=run_production_injection_imr_phenom

srun python \${JOB} ${OUTDIR}/\${SLURM_ARRAY_TASK_ID} \${SCRIPT} \${RECOVERY_MODEL} $@
EOF