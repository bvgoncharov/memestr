import numpy as np
import gwmemory
import copy
# import gwsurrogate as gws
from scipy.interpolate import CubicSpline
from scipy.signal.windows import tukey
from bilby.gw.source import lal_binary_black_hole
from bilby.gw.conversion import convert_to_lal_binary_black_hole_parameters
gamma_lmlm = gwmemory.angles.load_gamma()
roll_off = 0.2


def time_domain_nr_hyb_sur_waveform_with_memory(times, mass_ratio, total_mass, s13, s23,
                                                luminosity_distance, inc, phase, **kwargs):
    waveform = _evaluate_hybrid_surrogate(times=times, total_mass=total_mass, mass_ratio=mass_ratio, inc=inc,
                                          luminosity_distance=luminosity_distance, phase=phase, s13=s13, s23=s23,
                                          kwargs=kwargs)
    return apply_window(waveform=waveform, times=times, kwargs=kwargs)


def time_domain_nr_hyb_sur_waveform_with_memory_wrapped(times, mass_ratio, total_mass, s13, s23,
                                                        luminosity_distance, inc, phase, **kwargs):
    waveform = _evaluate_hybrid_surrogate(times=times, total_mass=total_mass, mass_ratio=mass_ratio, inc=inc,
                                          luminosity_distance=luminosity_distance, phase=phase, s13=s13, s23=s23,
                                          kwargs=kwargs)
    waveform = apply_window(waveform=waveform, times=times, kwargs=kwargs)
    return wrap_at_maximum(waveform=waveform, kwargs=kwargs)


def frequency_domain_IMRPhenomD_waveform_without_memory(frequencies, mass_ratio, total_mass, luminosity_distance,
                                                        s13, s23, inc, phase,
                                                        **kwargs):
    parameters = dict(mass_ratio=mass_ratio, total_mass=total_mass, luminosity_distance=luminosity_distance,
                      theta_jn=inc, phase=phase, chi_1=s13, chi_2=s23)
    parameters, _ = convert_to_lal_binary_black_hole_parameters(parameters)
    return lal_binary_black_hole(frequency_array=frequencies, **parameters, **kwargs)


def time_domain_IMRPhenomD_waveform_with_memory(times, mass_ratio, total_mass, luminosity_distance, s11, s12, s13,
                                                s21, s22, s23, inc, phase, **kwargs):
    waveform = _evaluate_imr_phenom_d_with_memory(times=times, total_mass=total_mass, mass_ratio=mass_ratio, inc=inc,
                                                  luminosity_distance=luminosity_distance, phase=phase, s11=s11,
                                                  s12=s12, s13=s13, s21=s21, s22=s22, s23=s23)

    return apply_window(waveform=waveform, times=times, kwargs=kwargs)


def time_domain_IMRPhenomD_waveform_with_memory_wrapped(times, mass_ratio, total_mass, luminosity_distance, s11, s12,
                                                        s13,
                                                        s21, s22, s23, inc, phase, **kwargs):
    waveform = _evaluate_imr_phenom_d_with_memory(times=times, total_mass=total_mass, mass_ratio=mass_ratio, inc=inc,
                                                  luminosity_distance=luminosity_distance, phase=phase, s11=s11,
                                                  s12=s12, s13=s13, s21=s21, s22=s22, s23=s23)
    waveform = apply_window(waveform=waveform, times=times, kwargs=kwargs)
    return wrap_at_maximum(waveform=waveform, kwargs=kwargs)


def time_domain_IMRPhenomD_waveform_without_memory(times, mass_ratio, total_mass, luminosity_distance, s11, s12, s13,
                                                   s21, s22, s23, inc, phase, **kwargs):
    waveform = _evaluate_imr_phenom_d_without_memory(times=times, total_mass=total_mass, mass_ratio=mass_ratio, inc=inc,
                                                     luminosity_distance=luminosity_distance, phase=phase, s11=s11,
                                                     s12=s12, s13=s13, s21=s21, s22=s22, s23=s23)
    return apply_window(waveform=waveform, times=times, kwargs=kwargs)


def time_domain_IMRPhenomD_waveform_without_memory_wrapped(times, mass_ratio, total_mass, luminosity_distance,
                                                           s11, s12, s13, s21, s22, s23, inc, phase, **kwargs):
    waveform = _evaluate_imr_phenom_d_without_memory(times=times, total_mass=total_mass, mass_ratio=mass_ratio, inc=inc,
                                                     luminosity_distance=luminosity_distance, phase=phase, s11=s11,
                                                     s12=s12, s13=s13, s21=s21, s22=s22, s23=s23)
    waveform = apply_window(waveform=waveform, times=times, kwargs=kwargs)
    return wrap_at_maximum(waveform=waveform, kwargs=kwargs)


def time_domain_IMRPhenomD_memory_waveform(times, mass_ratio, total_mass, luminosity_distance, s11, s12, s13,
                                           s21, s22, s23, inc, phase, **kwargs):
    temp_times = copy.copy(times)
    wave = gwmemory.waveforms.Approximant(name='IMRPhenomD',
                                          q=mass_ratio,
                                          MTot=total_mass,
                                          distance=luminosity_distance,
                                          S1=np.array([s11, s12, s13]),
                                          S2=np.array([s21, s22, s23]),
                                          times=temp_times)
    alpha = get_alpha(kwargs, times)
    window = tukey(M=len(times), alpha=alpha)
    memory, _ = wave.time_domain_memory(inc=inc, phase=phase, gamma_lmlm=gamma_lmlm)
    for mode in memory:
        memory[mode] *= window
    return memory


def _evaluate_hybrid_surrogate(times, total_mass, mass_ratio, inc, luminosity_distance, phase, s13, s23, kwargs):
    memory_generator = gwmemory.waveforms.HybridSurrogate(q=mass_ratio,
                                                          total_mass=total_mass,
                                                          spin_1=s13,
                                                          spin_2=s23,
                                                          times=times,
                                                          distance=luminosity_distance,
                                                          minimum_frequency=kwargs.get('mininum_frequency', 10),
                                                          sampling_frequency=kwargs.get('sampling_frequency', 2048),
                                                          units='mks'
                                                          )
    oscillatory, _ = memory_generator.time_domain_oscillatory(times=times, inc=inc, phase=phase)
    memory, _ = memory_generator.time_domain_memory(inc=inc, phase=phase, gamma_lmlm=gamma_lmlm)
    waveform = dict()
    for mode in memory:
        waveform[mode] = (memory[mode] + oscillatory[mode])
    return waveform


def _evaluate_imr_phenom_d_without_memory(times, total_mass, mass_ratio, inc, luminosity_distance, phase, s11, s12, s13,
                                          s21, s22, s23):
    temp_times = copy.copy(times)
    wave = gwmemory.waveforms.Approximant(name='IMRPhenomD',
                                          q=mass_ratio,
                                          MTot=total_mass,
                                          distance=luminosity_distance,
                                          S1=np.array([s11, s12, s13]),
                                          S2=np.array([s21, s22, s23]),
                                          times=temp_times)
    waveform = wave.time_domain_oscillatory(inc=inc, phase=phase)
    return waveform


def _evaluate_imr_phenom_d_with_memory(times, total_mass, mass_ratio, inc, luminosity_distance, phase, s11, s12, s13,
                                       s21, s22, s23):
    temp_times = copy.copy(times)
    wave = gwmemory.waveforms.Approximant(name='IMRPhenomD',
                                          q=mass_ratio,
                                          MTot=total_mass,
                                          distance=luminosity_distance,
                                          S1=np.array([s11, s12, s13]),
                                          S2=np.array([s21, s22, s23]),
                                          times=temp_times)
    oscillatory = wave.time_domain_oscillatory(inc=inc, phase=phase)
    memory, _ = wave.time_domain_memory(inc=inc, phase=phase, gamma_lmlm=gamma_lmlm)
    waveform = dict()
    for mode in memory:
        waveform[mode] = (memory[mode] + oscillatory[mode])
    return waveform


def get_alpha(kwargs, times):
    if 'alpha' in kwargs:
        if kwargs['alpha']:
            return kwargs['alpha']
    return roll_off / (times[-1] - times[0])


def apply_window(waveform, times, kwargs):
    alpha = get_alpha(kwargs, times)
    window = tukey(M=len(times), alpha=alpha)

    for mode in waveform:
        waveform[mode] *= window
    return waveform


def wrap_at_maximum(waveform, kwargs):
    max_index = np.argmax(np.abs(np.abs(waveform['plus']) + np.abs(waveform['cross'])))
    max_index_fd_model = kwargs.get('max_index_fd_model', len(waveform['plus']))
    shift = max_index_fd_model - max_index
    waveform = wrap_by_n_indices(shift=shift, waveform=waveform)
    return waveform, shift


def wrap_by_n_indices(shift, waveform):
    waveform['plus'] = np.roll(waveform['plus'], shift=shift)
    waveform['cross'] = np.roll(waveform['cross'], shift=shift)
    return waveform


def wrap_by_time_shift(waveforms, time_shifts, time_per_index):
    index_shifts = np.round(time_shifts / time_per_index).astype(int)
    return np.roll(waveforms, shift=index_shifts)


def wrap_by_time_shift_continuous(times, waveform, time_shift):
    waveform_interpolants = CubicSpline(times, waveform, extrapolate='periodic')
    new_times = times - time_shift
    return waveform_interpolants(new_times)
