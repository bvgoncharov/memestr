import bilby as bb
import memestr as me
from memestr.core.parameters import AllSettings
import logging


default_settings = AllSettings()


def expected_log_bf_vs_distance(luminosity_distances=None, distance_marginalization=False, **params):
    settings = AllSettings()
    parameters = settings.injection_parameters.__dict__
    parameters.update(params)

    sampling_frequency = settings.waveform_data.sampling_frequency
    duration = settings.waveform_data.duration
    start_time = settings.waveform_data.start_time

    logger = logging.getLogger('bilby')
    logger.disabled = True

    if luminosity_distances is None:
        luminosity_distances = [settings.injection_parameters.luminosity_distance]

    log_bfs = []
    for luminosity_distance in luminosity_distances:
        parameters['luminosity_distance'] = luminosity_distance
        log_bf = calculate_expected_log_bf(parameters, duration, sampling_frequency, start_time,
                                           distance_marginalization)
        print(str(luminosity_distance) + '\t:' + str(log_bf))
        log_bfs.append(log_bf)

    return luminosity_distances, log_bfs


def calculate_expected_log_bf(parameters,
                              duration=default_settings.waveform_data.duration,
                              sampling_frequency=default_settings.waveform_data.sampling_frequency,
                              start_time=default_settings.waveform_data.start_time,
                              distance_marginalization=False):
    waveform_generator_with_mem = bb.gw.WaveformGenerator(
        time_domain_source_model=me.core.waveforms.time_domain_IMRPhenomD_waveform_with_memory,
        sampling_frequency=sampling_frequency,
        duration=duration,
        start_time=start_time)
    waveform_generator_no_mem = bb.gw.WaveformGenerator(
        time_domain_source_model=me.core.waveforms.time_domain_IMRPhenomD_waveform_without_memory,
        sampling_frequency=sampling_frequency,
        duration=duration,
        start_time=start_time)
    ifos = bb.gw.detector.InterferometerList([])
    for name in ['H1', 'L1', 'V1']:
        interferometer = bb.gw.detector.get_empty_interferometer(name)
        # interferometer.power_spectral_density = bb.gw.detector.PowerSpectralDensity(asd_file='Aplus_asd.txt')
        interferometer.power_spectral_density = bb.gw.detector.\
            PowerSpectralDensity(psd_file='aLIGO_ZERO_DET_high_P_psd.txt')
        # interferometer.set_strain_data_from_zero_noise(
        #     sampling_frequency=sampling_frequency, duration=duration,
        #     start_time=start_time)
        interferometer.set_strain_data_from_power_spectral_density(
            sampling_frequency=sampling_frequency, duration=duration,
            start_time=start_time)

        interferometer.inject_signal(parameters=parameters,
                                     waveform_generator=waveform_generator_with_mem)
        ifos.append(interferometer)

    likelihood_with_mem = \
        bb.gw.likelihood.GravitationalWaveTransient(interferometers=ifos,
                                                    waveform_generator=waveform_generator_with_mem,
                                                    priors=dict(luminosity_distance=
                                                                bb.gw.prior.
                                                                UniformComovingVolume(10, 5000,
                                                                                      name='luminosity_distance')),
                                                    distance_marginalization=distance_marginalization)
    likelihood_no_mem = \
        bb.gw.likelihood.GravitationalWaveTransient(interferometers=ifos,
                                                    waveform_generator=waveform_generator_no_mem,
                                                    priors=dict(luminosity_distance=
                                                                bb.gw.prior.
                                                                UniformComovingVolume(10, 5000,
                                                                                      name='luminosity_distance')),
                                                    distance_marginalization=distance_marginalization)
    likelihood_with_mem.parameters = parameters
    likelihood_no_mem.parameters = parameters
    return likelihood_with_mem.log_likelihood() - likelihood_no_mem.log_likelihood()
