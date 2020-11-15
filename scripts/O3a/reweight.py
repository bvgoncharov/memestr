import pickle
import numpy as np
from collections import namedtuple
import matplotlib.pyplot as plt
import sys
from scipy.special import logsumexp

import bilby

import memestr


Event = namedtuple("Event", ["time_tag", "name", "detectors"])

events = [
    Event(time_tag="1126259462-391", name="GW150914", detectors="H1L1"),
    Event(time_tag="1128678900-4", name="GW151012", detectors="H1L1"),
    Event(time_tag="1135136350-6", name="GW151226", detectors="H1L1"),
    Event(time_tag="1167559936-6", name="GW170104", detectors="H1L1"),
    Event(time_tag="1180922494-5", name="GW170608", detectors="H1L1"),
    Event(time_tag="1185389807-3", name="GW170729", detectors="H1L1V1"),
    Event(time_tag="1186302519-7", name="GW170809", detectors="H1L1V1"),
    Event(time_tag="1186741861-5", name="GW170814", detectors="H1L1V1"),
    Event(time_tag="1187058327-1", name="GW170818", detectors="H1L1V1"),
    Event(time_tag="1187529256-5", name="GW170823", detectors="H1L1"),
    Event(time_tag="1238782700-3", name="GW190408A", detectors="H1L1V1"),
    Event(time_tag="1239082262-2", name="GW190412", detectors="H1L1V1"),
    Event(time_tag="1239168612-5", name="GW190413A", detectors="H1L1V1"),
    Event(time_tag="1239198206-7", name="GW190413B", detectors="H1L1V1"),
    Event(time_tag="1239917954-3", name="GW190421A", detectors="H1L1"),
    Event(time_tag="1240164426-1", name="GW190424A", detectors="L1"),
    Event(time_tag="1240327333-3", name="GW190426A", detectors="H1L1V1"),
    Event(time_tag="1240944862-3", name="GW190503A", detectors="H1L1V1"),
    Event(time_tag="1241719652-4", name="GW190512A", detectors="H1L1V1"),
    Event(time_tag="1241816086-8", name="GW190513A", detectors="H1L1V1"),
    Event(time_tag="1241852074-8", name="GW190514A", detectors="H1L1"),
    Event(time_tag="1242107479-8", name="GW190517A", detectors="H1L1V1"),
    Event(time_tag="1242315362-4", name="GW190519A", detectors="H1L1V1"),
    Event(time_tag="1242442967-4", name="GW190521", detectors="H1L1V1"),
    Event(time_tag="1242459857-5", name="GW190521A", detectors="H1L1"),
    Event(time_tag="1242984073-8", name="GW190527A", detectors="H1L1"),
    Event(time_tag="1243533585-1", name="GW190602A", detectors="H1L1V1"),
    Event(time_tag="1245035079-3", name="GW190620A", detectors="L1V1"),
    Event(time_tag="1245955943-2", name="GW190630A", detectors="L1V1"),
    Event(time_tag="1246048404-6", name="GW190701A", detectors="H1L1V1"),
    Event(time_tag="1246487219-3", name="GW190706A", detectors="H1L1V1"),
    Event(time_tag="1246527224-2", name="GW190707A", detectors="H1L1"),
    Event(time_tag="1246663515-4", name="GW190708A", detectors="L1V1"),
    Event(time_tag="1247608532-9", name="GW190719A", detectors="H1L1"),
    Event(time_tag="1247616534-7", name="GW190720A", detectors="H1L1V1"),
    Event(time_tag="1248242632-0", name="GW190727A", detectors="H1L1V1"),
    Event(time_tag="1248331528-5", name="GW190728A", detectors="H1L1V1"),
    Event(time_tag="1248617394-6", name="GW190731A", detectors="H1L1"),
    Event(time_tag="1248834439-9", name="GW190803A", detectors="H1L1V1"),
    Event(time_tag="1249852257-0", name="GW190814", detectors="L1V1"),
    Event(time_tag="1251009263-8", name="GW190828A", detectors="H1L1V1"),
    Event(time_tag="1251010527-9", name="GW190828B", detectors="H1L1V1"),
    Event(time_tag="1252064527-7", name="GW190909A", detectors="H1L1"),
    Event(time_tag="1252150105-3", name="GW190910A", detectors="L1V1"),
    Event(time_tag="1252627040-7", name="GW190915A", detectors="H1L1V1"),
    Event(time_tag="1253326744-8", name="GW190924A", detectors="H1L1V1"),
    Event(time_tag="1253755327-5", name="GW190929A", detectors="H1L1V1"),
    Event(time_tag="1253885759-2", name="GW190930A", detectors="H1L1")
]

event_number = int(sys.argv[1])
# event_number = 0
time_tag = events[event_number].time_tag
event = events[event_number].name
detectors = events[event_number].detectors
# suffix = "fast"
# result = bilby.core.result.read_in_result(f'{event}_{suffix}/result/run_data0_{time_tag}_analysis_{detectors}_dynesty_merge_result.json')
result = bilby.core.result.read_in_result(f'{event}/result/run_data0_{time_tag}_analysis_{detectors}_dynesty_merge_result.json')
# result.outdir = f'{event}_{suffix}/result/'
result.outdir = f'{event}/result/'
result.plot_corner()
print(len(result.posterior))

# with open(f'{event}_{suffix}/data/run_data0_{time_tag}_generation_data_dump.pickle', "rb") as f:
with open(f'{event}/data/run_data0_{time_tag}_generation_data_dump.pickle', "rb") as f:
    data_dump = pickle.load(f)
ifos = data_dump.interferometers
bilby.core.utils.logger.disabled = True
wg_xhm_fast = bilby.gw.waveform_generator.WaveformGenerator(
    sampling_frequency=ifos.sampling_frequency, duration=ifos.duration,
    frequency_domain_source_model=memestr.core.waveforms.fd_imrx_fast)

wg_xhm = bilby.gw.waveform_generator.WaveformGenerator(
    sampling_frequency=ifos.sampling_frequency, duration=ifos.duration,
    frequency_domain_source_model=memestr.core.waveforms.fd_imrx)

wg_xhm_memory = bilby.gw.waveform_generator.WaveformGenerator(
    sampling_frequency=ifos.sampling_frequency, duration=ifos.duration,
    frequency_domain_source_model=memestr.core.waveforms.fd_imrx_with_memory)

bilby.core.utils.logger.disabled = False


likelihood_xhm_osc = bilby.gw.likelihood.GravitationalWaveTransient(
    interferometers=ifos, waveform_generator=wg_xhm_fast)
likelihood_xhm_ref = bilby.gw.likelihood.GravitationalWaveTransient(
    interferometers=ifos, waveform_generator=wg_xhm)
likelihood_xhm_memory = bilby.gw.likelihood.GravitationalWaveTransient(
    interferometers=ifos, waveform_generator=wg_xhm_memory)

try:
    log_memory_weights = np.loadtxt(f"{event}_memory_log_weights")
except Exception:
    reweighted_time_shift_memory_log_bf, log_memory_weights = memestr.core.postprocessing.reweigh_by_likelihood(
        new_likelihood=likelihood_xhm_memory, result=result,
        reference_likelihood=likelihood_xhm_osc, use_stored_likelihood=True)
    np.savetxt(f"{event}_memory_log_weights", log_memory_weights)

reweighted_memory_log_bf = logsumexp(log_memory_weights) - np.log(len(log_memory_weights))


n_eff_memory = np.sum(np.exp(log_memory_weights)) ** 2 / np.sum(np.exp(log_memory_weights) ** 2)
print(n_eff_memory)
print(reweighted_memory_log_bf)
