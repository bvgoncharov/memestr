import copy

import bilby
import gwmemory
import numpy as np

from memestr.core.waveforms import convert_to_frequency_domain
from .utils import apply_window, gamma_lmlm


# def frequency_domain_IMRPhenomD_waveform_without_memory(frequencies, mass_ratio, total_mass, luminosity_distance,
#                                                         s13, s23, inc, phase,
#                                                         **kwargs):
#     parameters = dict(mass_ratio=mass_ratio, total_mass=total_mass, luminosity_distance=luminosity_distance,
#                       theta_jn=inc, phase=phase, chi_1=s13, chi_2=s23)
#     parameters, _ = convert_to_lal_binary_black_hole_parameters(parameters)
#     return lal_binary_black_hole(frequency_array=frequencies, **parameters, **kwargs)


def frequency_domain_IMRPhenomD_waveform_with_memory(frequencies, mass_ratio, total_mass, luminosity_distance,
                                                     s13, s23, inc, phase, **kwargs):
    series = bilby.core.series.CoupledTimeAndFrequencySeries(start_time=0)
    series.frequency_array = frequencies
    waveform, memory, memory_generator = _evaluate_imr_phenom_d(series.time_array, total_mass=total_mass,
                                                                mass_ratio=mass_ratio, inc=inc,
                                                                luminosity_distance=luminosity_distance, phase=phase,
                                                                s13=s13, s23=s23, fold_in_memory=True)
    for mode in memory:
        waveform[mode] += memory[mode]
    return convert_to_frequency_domain(memory_generator, series, waveform, **kwargs)


def frequency_domain_IMRPhenomD_waveform_without_memory(frequencies, mass_ratio, total_mass, luminosity_distance,
                                                        s13, s23,
                                                        inc, phase, **kwargs):
    series = bilby.core.series.CoupledTimeAndFrequencySeries(start_time=0)
    series.frequency_array = frequencies
    waveform, memory_generator = _evaluate_imr_phenom_d(series.time_array, total_mass=total_mass,
                                                        mass_ratio=mass_ratio, inc=inc,
                                                        luminosity_distance=luminosity_distance, phase=phase,
                                                        s13=s13, s23=s23, fold_in_memory=False)
    return convert_to_frequency_domain(memory_generator, series, waveform, **kwargs)


def time_domain_IMRPhenomD_waveform_with_memory(times, mass_ratio, total_mass, luminosity_distance, s13,
                                                s23, inc, phase, **kwargs):
    waveform, memory, _ = _evaluate_imr_phenom_d(times=times, total_mass=total_mass, mass_ratio=mass_ratio, inc=inc,
                                                 luminosity_distance=luminosity_distance, phase=phase,
                                                 s13=s13, s23=s23, fold_in_memory=True)
    for mode in waveform:
        waveform[mode] += memory[mode]
    return apply_window(waveform=waveform, times=times, kwargs=kwargs)


def time_domain_IMRPhenomD_waveform_without_memory(times, mass_ratio, total_mass, luminosity_distance,
                                                   s13, s23, inc, phase, **kwargs):
    waveform, _ = _evaluate_imr_phenom_d(times=times, total_mass=total_mass, mass_ratio=mass_ratio, inc=inc,
                                         luminosity_distance=luminosity_distance, phase=phase,
                                         s13=s13, s23=s23, fold_in_memory=False)
    return apply_window(waveform=waveform, times=times, kwargs=kwargs)


def time_domain_IMRPhenomD_memory_waveform(times, mass_ratio, total_mass, luminosity_distance,
                                           s13, s23, inc, phase, **kwargs):
    _, memory, _ = _evaluate_imr_phenom_d(times=times, total_mass=total_mass,
                                          mass_ratio=mass_ratio, inc=inc,
                                          luminosity_distance=luminosity_distance, phase=phase,
                                          s13=s13, s23=s23, fold_in_memory=True)
    return apply_window(waveform=memory, times=times, kwargs=kwargs)


def _evaluate_imr_phenom_d(times, total_mass, mass_ratio, inc, luminosity_distance, phase,
                           s13, s23, fold_in_memory=True):
    temp_times = copy.copy(times)
    memory_generator = gwmemory.waveforms.Approximant(name='IMRPhenomD',
                                                      q=mass_ratio,
                                                      MTot=total_mass,
                                                      distance=luminosity_distance,
                                                      S1=np.array([0., 0., s13]),
                                                      S2=np.array([0., 0., s23]),
                                                      times=temp_times)
    oscillatory = memory_generator.time_domain_oscillatory(inc=inc, phase=phase)
    if not fold_in_memory:
        return oscillatory, memory_generator
    else:
        memory, _ = memory_generator.time_domain_memory(inc=inc, phase=phase, gamma_lmlm=gamma_lmlm)
        return oscillatory, memory, memory_generator
