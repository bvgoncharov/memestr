import memestr.wrappers as wrappers
import memestr.core as core

models = dict(
    time_domain_IMRPhenomD_memory_waveform=core.waveforms.time_domain_IMRPhenomD_memory_waveform,
    time_domain_IMRPhenomD_waveform_with_memory=core.waveforms.time_domain_IMRPhenomD_waveform_with_memory,
    time_domain_IMRPhenomD_waveform_without_memory=core.waveforms.time_domain_IMRPhenomD_waveform_without_memory,
    time_domain_IMRPhenomD_waveform_without_memory_wrapped=core.waveforms.time_domain_IMRPhenomD_waveform_without_memory_wrapped,
    time_domain_nr_hyb_sur_waveform_with_memory=core.waveforms.time_domain_nr_hyb_sur_waveform_with_memory,
    time_domain_nr_hyb_sur_waveform_with_memory_wrapped=core.waveforms.time_domain_nr_hyb_sur_waveform_with_memory_wrapped,
    time_domain_nr_hyb_sur_waveform_without_memory_wrapped_no_shift_return=core.waveforms.time_domain_nr_hyb_sur_waveform_without_memory_wrapped_no_shift_return,
    frequency_domain_IMRPhenomD_waveform_without_memory=core.waveforms.frequency_domain_IMRPhenomD_waveform_without_memory
)

scripts = dict(
    run_production_injection_imr_phenom=wrappers.injection_recovery.run_production_injection_imr_phenom,
    run_basic_injection_imr_phenom=wrappers.injection_recovery.run_basic_injection_imr_phenom,
)
