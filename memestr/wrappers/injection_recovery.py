from __future__ import division

import numpy as np
import time
import bilby
import logging

from memestr.core.parameters import AllSettings, InjectionParameters


def run_basic_injection(injection_model, recovery_model, outdir, **kwargs):
    logger = logging.getLogger('bilby')

    settings = AllSettings.from_defaults_with_some_specified_kwargs(**kwargs)
    settings.waveform_data.start_time = settings.injection_parameters.geocent_time + 2 - settings.waveform_data.duration
    np.random.seed(settings.other_settings.random_seed)
    logger.info("Random seed: " + str(settings.other_settings.random_seed))

    bilby.core.utils.setup_logger(outdir=outdir, label=settings.sampler_settings.label)

    waveform_generator = bilby.gw.WaveformGenerator(time_domain_source_model=injection_model,
                                                    parameters=settings.injection_parameters.__dict__,
                                                    waveform_arguments=settings.waveform_arguments.__dict__,
                                                    **settings.waveform_data.__dict__)

    hf_signal = waveform_generator.frequency_domain_strain()
    ifos = [_get_ifo(hf_signal, name, outdir, settings, waveform_generator)
            for name in settings.detector_settings.detectors]
    ifos = bilby.gw.detector.InterferometerList(ifos)

    waveform_generator.time_domain_source_model = recovery_model

    priors = settings.recovery_priors.proper_dict()
    likelihood = bilby.gw.likelihood \
        .GravitationalWaveTransient(interferometers=ifos,
                                    waveform_generator=waveform_generator,
                                    priors=priors,
                                    time_marginalization=settings.other_settings.time_marginalization,
                                    distance_marginalization=settings.other_settings.distance_marginalization,
                                    phase_marginalization=settings.other_settings.phase_marginalization)

    likelihood.parameters = settings.injection_parameters.__dict__
    logger.info('Sampler settings: ' + str(settings.sampler_settings))
    logger.info('Waveform data: ' + str(settings.waveform_data))
    logger.info("Log Likelihood at injected value: " + str(likelihood.log_likelihood_ratio()))
    np.random.seed(int(time.time()))
    result = bilby.core.sampler.run_sampler(likelihood=likelihood,
                                            priors=priors,
                                            conversion_function=bilby.gw.conversion.generate_all_bbh_parameters,
                                            injection_parameters=settings.injection_parameters.__dict__,
                                            outdir=outdir,
                                            save=True,
                                            verbose=True,
                                            random_seed=np.random.randint(0, 1000),
                                            **settings.sampler_settings.__dict__)
    result.plot_corner(lionize=settings.other_settings.lionize)
    logger.info(str(result))
    result.save_to_file()
    return result


def _get_ifo(hf_signal, name, outdir, settings, waveform_generator):
    interferometer = bilby.gw.detector.get_empty_interferometer(name)
    if name in ['H1', 'L1']:
        interferometer.power_spectral_density = bilby.gw.detector.PowerSpectralDensity.from_aligo()
    elif name in ['V1']:
        interferometer.power_spectral_density = bilby.gw.detector.PowerSpectralDensity. \
            from_power_spectral_density_file('AdV_psd.txt')
    if settings.detector_settings.zero_noise:
        interferometer.set_strain_data_from_zero_noise(**settings.waveform_data.__dict__)
    else:
        interferometer.set_strain_data_from_power_spectral_density(**settings.waveform_data.__dict__)
    injection_polarizations = interferometer.inject_signal(
        parameters=settings.injection_parameters.__dict__,
        injection_polarizations=hf_signal,
        waveform_generator=waveform_generator)
    signal = interferometer.get_detector_response(
        injection_polarizations, settings.injection_parameters.__dict__)
    interferometer.plot_data(signal=signal, outdir=outdir)
    interferometer.save_data(outdir)
    return interferometer


def update_kwargs(default_kwargs, kwargs):
    new_kwargs = default_kwargs.copy()
    for key in list(set(default_kwargs.keys()).intersection(kwargs.keys())):
        new_kwargs[key] = kwargs[key]
    return new_kwargs


def run_basic_injection_nrsur(injection_model, recovery_model, outdir, **kwargs):
    start_time = -0.5
    end_time = 0.0  # 0.029
    duration = end_time - start_time

    priors = dict()
    injection_parameters = InjectionParameters.init_with_updated_kwargs(**kwargs)
    for key in injection_parameters.__dict__:
        priors['prior_' + key] = injection_parameters.__dict__[key]
    # priors['prior_total_mass'] = bilby.core.prior.Uniform(minimum=50, maximum=70, latex_label="$M_{tot}$")
    # priors['prior_mass_ratio'] = bilby.core.prior.Uniform(minimum=1, maximum=2, latex_label="$q$")
    # priors['prior_luminosity_distance'] = bilby.gw.prior.UniformComovingVolume(name='luminosity_distance', minimum=1e1,
    #                                                                            maximum=5e3, latex_label="$L_D$")
    # priors['prior_inc'] = bilby.core.prior.Uniform(minimum=0, maximum=np.pi, latex_label="$\iota$")
    priors['prior_phase'] = bilby.core.prior.Uniform(name='phase', minimum=0, maximum=np.pi, latex_label="$\phi$")
    # priors['prior_ra'] = bilby.core.prior.Uniform(name='ra', minimum=0, maximum=2 * np.pi, latex_label="$RA$")
    # priors['prior_dec'] = bilby.core.prior.Cosine(name='dec', latex_label="$DEC$")
    priors['prior_psi'] = bilby.core.prior.Uniform(name='psi', minimum=0, maximum=np.pi, latex_label="$\psi$")
    # priors['prior_geocent_time'] = bilby.core.prior.Uniform(1126259642.322, 1126259642.522, name='geocent_time')
    nr_sur_kwargs = dict(
        start_time=start_time,
        duration=duration,
        label='NRSur',
        new_seed=True,
        zero_noise=False
    )
    nr_sur_kwargs.update(priors)
    nr_sur_kwargs.update(kwargs)
    return run_basic_injection(injection_model=injection_model, recovery_model=recovery_model, outdir=outdir,
                               **nr_sur_kwargs)


def run_basic_injection_imr_phenom(injection_model, recovery_model, outdir, **kwargs):
    priors = dict()
    injection_parameters = InjectionParameters.init_with_updated_kwargs(**kwargs)
    for key in injection_parameters.__dict__:
        priors['prior_' + key] = injection_parameters.__dict__[key]
    priors['prior_total_mass'] = bilby.core.prior.Uniform(minimum=np.maximum(injection_parameters.total_mass - 20, 15),
                                                          maximum=injection_parameters.total_mass + 30,
                                                          latex_label="$M_{tot}$")
    priors['prior_mass_ratio'] = bilby.core.prior.Uniform(minimum=np.maximum(injection_parameters.mass_ratio-0.5, 0.4),
                                                          maximum=1,
                                                          latex_label="$q$")
    priors['prior_luminosity_distance'] = bilby.gw.prior.UniformComovingVolume(minimum=10,
                                                                               maximum=5000,
                                                                               latex_label="$L_D$",
                                                                               name='luminosity_distance')
    priors['prior_inc'] = bilby.core.prior.Sine(latex_label="$\theta_{jn}$")
    priors['prior_ra'] = bilby.core.prior.Uniform(minimum=0, maximum=2*np.pi, latex_label="$RA$")
    priors['prior_dec'] = bilby.core.prior.Cosine(latex_label="$DEC$")
    priors['prior_phase'] = bilby.core.prior.Uniform(minimum=0,
                                                     maximum=2*np.pi,
                                                     latex_label="$\phi$")
    priors['prior_psi'] = bilby.core.prior.Uniform(minimum=0,
                                                   maximum=np.pi,
                                                   latex_label="$\psi$")
    priors['prior_geocent_time'] = bilby.core.prior.Uniform(minimum=injection_parameters.geocent_time - 0.1,
                                                            maximum=injection_parameters.geocent_time + 0.1,
                                                            latex_label='$t_c$')

    imr_phenom_kwargs = dict(
        label='IMRPhenomD'
    )
    imr_phenom_kwargs.update(priors)
    imr_phenom_kwargs.update(kwargs)
    return run_basic_injection(injection_model=injection_model, recovery_model=recovery_model, outdir=outdir,
                               **imr_phenom_kwargs)
