#!/usr/bin/env bash

source production_IMR_time_phase_setup.sh ${0} ${1}

sbatch ${JOB_NAME} ${OUTPUT} ${TIME} ${NTASKS} ${MEM_PER_CPU} ${CPUS_PER_TASK} ${EMAIL} ${ARRAY}<<EOF
#!/usr/bin/env bash
srun python run.py ${OUTDIR}/\${SLURM_ARRAY_TASK_ID} run_time_phase_optimization $@
EOF