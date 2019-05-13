from __future__ import division

import numpy as np
import time
import bilby
import logging
from copy import deepcopy

from memestr.core.parameters import AllSettings, InjectionParameters
from memestr.core.utils import get_ifo
from memestr.core.submit import get_injection_parameter_set
from memestr.core.postprocessing import adjust_phase_and_geocent_time_complete_posterior_proper, \
    reweigh_by_two_likelihoods, reweigh_by_likelihood
from memestr.core.waveforms import time_domain_nr_hyb_sur_waveform_with_memory_wrapped, \
    time_domain_nr_hyb_sur_waveform_without_memory_wrapped

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
    # import matplotlib.pyplot as plt
    # tds = waveform_generator.time_domain_strain(parameters=settings.injection_parameters.__dict__)['plus']
    # fds = np.abs(np.sqrt(waveform_generator.frequency_domain_strain(parameters=settings.injection_parameters.__dict__)['plus']**2 + \
    #       waveform_generator.frequency_domain_strain(parameters=settings.injection_parameters.__dict__)['cross']**2))
    # plt.plot(waveform_generator.time_array, tds)
    # plt.show()
    # plt.clf()
    # plt.loglog()
    # plt.plot(waveform_generator.frequency_array, fds)
    # plt.show()
    # plt.clf()

    hf_signal = waveform_generator.frequency_domain_strain()
    ifos = [get_ifo(hf_signal, name, outdir, settings, waveform_generator, label='TD_model')
            for name in settings.detector_settings.detectors]
    ifos = bilby.gw.detector.InterferometerList(ifos)

    waveform_generator = bilby.gw.WaveformGenerator(frequency_domain_source_model=recovery_model,
                                                    parameters=settings.injection_parameters.__dict__,
                                                    waveform_arguments=settings.waveform_arguments.__dict__,
                                                    **settings.waveform_data.__dict__)
    # tds = waveform_generator.time_domain_strain(parameters=settings.injection_parameters.__dict__)['plus']
    # fds = np.abs(np.sqrt(waveform_generator.frequency_domain_strain(parameters=settings.injection_parameters.__dict__)['plus']**2 + \
    #       waveform_generator.frequency_domain_strain(parameters=settings.injection_parameters.__dict__)['cross']**2))
    # plt.plot(waveform_generator.time_array, tds)
    # plt.show()
    # plt.clf()
    # plt.loglog()
    # plt.plot(waveform_generator.frequency_array, fds)
    # plt.show()
    # plt.clf()

    priors = settings.recovery_priors.proper_dict()
    likelihood = bilby.gw.likelihood \
        .GravitationalWaveTransient(interferometers=ifos,
                                    waveform_generator=waveform_generator,
                                    priors=priors,
                                    time_marginalization=settings.other_settings.time_marginalization,
                                    distance_marginalization=settings.other_settings.distance_marginalization,
                                    phase_marginalization=settings.other_settings.phase_marginalization)
    likelihood.parameters = deepcopy(settings.injection_parameters.__dict__)
    logger.info("Log Likelihood ratio at injected value: " + str(likelihood.log_likelihood_ratio()))
    logger.info("Log Likelihood at injected value: " + str(likelihood.log_likelihood()))
    np.random.seed(int(time.time()))
    result = bilby.core.sampler.run_sampler(likelihood=likelihood,
                                            priors=priors,
                                            injection_parameters=deepcopy(settings.injection_parameters.__dict__),
                                            outdir=outdir,
                                            save=True,
                                            verbose=True,
                                            random_seed=np.random.randint(0, 100000),
                                            # sampler=settings.sampler_settings.sampler,
                                            sampler='dynesty',
                                            npoints=settings.sampler_settings.npoints,
                                            # npoints=3000,
                                            walks=10,
                                            label=settings.sampler_settings.label,
                                            clean=settings.sampler_settings.clean,
                                            nthreads=settings.sampler_settings.nthreads,
                                            # dlogz=0.1,
                                            dlogz=settings.sampler_settings.dlogz,
                                            maxmcmc=settings.sampler_settings.maxmcmc,
                                            resume=settings.sampler_settings.resume)
    result.save_to_file()
    result.plot_corner(lionize=settings.other_settings.lionize)
    logger.info(str(result))
    result.posterior = bilby.gw.conversion.generate_posterior_samples_from_marginalized_likelihood(result.posterior, likelihood)
    result.save_to_file()
    result.plot_corner(lionize=settings.other_settings.lionize)
    logger.info(str(result))
    return result


def update_kwargs(default_kwargs, kwargs):
    new_kwargs = default_kwargs.copy()
    for key in list(set(default_kwargs.keys()).intersection(kwargs.keys())):
        new_kwargs[key] = kwargs[key]
    return new_kwargs


def run_basic_injection_imr_phenom(injection_model, recovery_model, outdir, **kwargs):
    priors = dict()
    injection_parameters = InjectionParameters.init_with_updated_kwargs(**kwargs)
    for key in injection_parameters.__dict__:
        priors['prior_' + key] = injection_parameters.__dict__[key]
    # priors['prior_total_mass'] = bilby.core.prior.Uniform(minimum=np.maximum(injection_parameters.total_mass - 20, 15),
    #                                                       maximum=injection_parameters.total_mass + 30,
    #                                                       latex_label="$M_{tot}$")
    # priors['prior_mass_ratio'] = bilby.core.prior.Uniform(minimum=np.maximum(injection_parameters.mass_ratio-0.5, 0.6),
    #                                                       maximum=1,
    #                                                       latex_label="$q$")
    # priors['prior_luminosity_distance'] = bilby.gw.prior.UniformComovingVolume(minimum=10,
    #                                                                            maximum=5000,
    #                                                                            latex_label="$L_D$",
    #                                                                            name='luminosity_distance')
    # priors['prior_inc'] = bilby.core.prior.Sine(latex_label="$\\theta_{jn}$")
    # priors['prior_ra'] = bilby.core.prior.Uniform(minimum=0, maximum=2*np.pi, latex_label="$RA$")
    # priors['prior_dec'] = bilby.core.prior.Cosine(latex_label="$DEC$")
    priors['prior_phase'] = bilby.core.prior.Uniform(minimum=0,
                                                     maximum=2*np.pi,
                                                     latex_label="$\phi$")
    # priors['prior_psi'] = bilby.core.prior.Uniform(minimum=0,
    #                                                maximum=np.pi,
    #                                                latex_label="$\psi$")
    priors['prior_geocent_time'] = bilby.core.prior.Uniform(minimum=injection_parameters.geocent_time - 0.5,
                                                            maximum=injection_parameters.geocent_time + 0.5,
                                                            latex_label='$t_c$')
    priors['prior_s13'] = bilby.gw.prior.AlignedSpin(name='s13', a_prior=bilby.core.prior.Uniform(0.0, 0.5),
                                                     latex_label='s13')
    priors['prior_s23'] = bilby.gw.prior.AlignedSpin(name='s23', a_prior=bilby.core.prior.Uniform(0.0, 0.5),
                                                     latex_label='s23')

    imr_phenom_kwargs = dict(
        label='IMRPhenomD'
    )
    imr_phenom_kwargs.update(priors)
    imr_phenom_kwargs.update(kwargs)
    return run_basic_injection(injection_model=injection_model, recovery_model=recovery_model, outdir=outdir,
                               **imr_phenom_kwargs)


def run_production_injection_imr_phenom(injection_model, recovery_model, outdir, **kwargs):
    priors = dict()
    filename_base = str(kwargs.get('filename_base', 0))
    filename_base = filename_base.replace('_dynesty', '')
    filename_base = filename_base.replace('_cpnest', '')
    filename_base = filename_base.replace('_pypolychord', '')

    injection_parameters = get_injection_parameter_set(filename_base)
    for key in injection_parameters:
        priors['prior_' + key] = injection_parameters[key]
    priors['prior_total_mass'] = bilby.core.prior.Uniform(minimum=np.maximum(injection_parameters['total_mass'] - 20, 15),
                                                          maximum=injection_parameters['total_mass'] + 30,
                                                          latex_label="$M_{tot}$")
    priors['prior_mass_ratio'] = bilby.core.prior.Uniform(minimum=np.maximum(injection_parameters['mass_ratio']-0.5, 0.4),
                                                          maximum=1,
                                                          latex_label="$q$")
    priors['prior_luminosity_distance'] = bilby.gw.prior.UniformComovingVolume(minimum=10,
                                                                               maximum=5000,
                                                                               latex_label="$L_D$",
                                                                               name='luminosity_distance')
    priors['prior_inc'] = bilby.core.prior.Sine(latex_label="$\\theta_{jn}$")
    priors['prior_ra'] = bilby.core.prior.Uniform(minimum=0, maximum=2*np.pi, latex_label="$RA$")
    priors['prior_dec'] = bilby.core.prior.Cosine(latex_label="$DEC$")
    priors['prior_phase'] = bilby.core.prior.Uniform(minimum=0,
                                                     maximum=2*np.pi,
                                                     latex_label="$\phi$")
    priors['prior_psi'] = bilby.core.prior.Uniform(minimum=0,
                                                   maximum=np.pi,
                                                   latex_label="$\psi$")
    priors['prior_geocent_time'] = bilby.core.prior.Uniform(minimum=injection_parameters['geocent_time'] - 0.5,
                                                            maximum=injection_parameters['geocent_time'] + 0.5,
                                                            latex_label='$t_c$')
    priors['prior_s13'] = bilby.gw.prior.AlignedSpin(name='s13', a_prior=bilby.core.prior.Uniform(0.0, 0.5),
                                                     latex_label='s13')
    priors['prior_s23'] = bilby.gw.prior.AlignedSpin(name='s23', a_prior=bilby.core.prior.Uniform(0.0, 0.5),
                                                     latex_label='s23')

    imr_phenom_kwargs = dict(
        label='IMRPhenomD'
    )
    imr_phenom_kwargs.update(priors)
    imr_phenom_kwargs.update(kwargs)
    return run_production_recovery(recovery_model=recovery_model, outdir=outdir, **imr_phenom_kwargs,
                                   **injection_parameters)


def run_production_recovery(recovery_model, outdir, **kwargs):
    logger = logging.getLogger('bilby')

    settings = AllSettings.from_defaults_with_some_specified_kwargs(**kwargs)
    settings.waveform_data.start_time = settings.injection_parameters.geocent_time + 2 - settings.waveform_data.duration

    bilby.core.utils.setup_logger(outdir=outdir, label=settings.sampler_settings.label)
    filename_base = str(kwargs.get('filename_base', 0))
    filename_base = filename_base.replace('_dynesty', '')
    filename_base = filename_base.replace('_cpnest', '')
    filename_base = filename_base.replace('_pypolychord', '')

    ifos = bilby.gw.detector.InterferometerList.from_hdf5('parameter_sets/' +
                                                          str(filename_base) +
                                                          '_H1L1V1.h5')
    # import deepdish
    # ifos = deepdish.io.load('parameter_sets/' + str(filename_base) + '_H1L1V1.h5')
    # for i, ifo in enumerate(ifos):
    #     ifos[i].strain_data = ifo._strain_data
    # ifos = bilby.gw.detector.InterferometerList(ifos)
    # # ifos.plot_data()
    waveform_generator = bilby.gw.WaveformGenerator(frequency_domain_source_model=recovery_model,
                                                    parameters=settings.injection_parameters.__dict__,
                                                    waveform_arguments=settings.waveform_arguments.__dict__,
                                                    **settings.waveform_data.__dict__)

    priors = settings.recovery_priors.proper_dict()
    likelihood_imr_phenom = bilby.gw.likelihood \
        .GravitationalWaveTransient(interferometers=ifos,
                                    waveform_generator=waveform_generator,
                                    priors=priors,
                                    time_marginalization=settings.other_settings.time_marginalization,
                                    distance_marginalization=settings.other_settings.distance_marginalization,
                                    phase_marginalization=settings.other_settings.phase_marginalization)
    likelihood_imr_phenom.parameters = deepcopy(settings.injection_parameters.__dict__)
    np.random.seed(int(time.time()))
    logger.info('Injection Parameters')
    logger.info(str(settings.injection_parameters))
    result = bilby.core.sampler.run_sampler(likelihood=likelihood_imr_phenom,
                                            priors=priors,
                                            injection_parameters=deepcopy(settings.injection_parameters.__dict__),
                                            outdir=outdir,
                                            save=True,
                                            verbose=True,
                                            random_seed=np.random.randint(0, 100000),
                                            sampler=settings.sampler_settings.sampler,
                                            npoints=settings.sampler_settings.npoints,
                                            walks=100,
                                            label=settings.sampler_settings.label,
                                            clean=settings.sampler_settings.clean,
                                            nthreads=settings.sampler_settings.nthreads,
                                            maxmcmc=settings.sampler_settings.maxmcmc,
                                            resume=settings.sampler_settings.resume,
                                            save_bounds=False,
                                            check_point_plot=True,
                                            n_check_point=1000)
    result.save_to_file()
    logger.info(str(result))
    # result = bilby.result.read_in_result(filename=str(filename_base) + '_pypolychord_production_IMR_non_mem_rec/IMR_mem_inj_non_mem_rec_result.json')
    result.posterior = bilby.gw.conversion.\
        generate_posterior_samples_from_marginalized_likelihood(result.posterior, likelihood_imr_phenom)
    result.save_to_file()
    params = deepcopy(settings.injection_parameters.__dict__)
    del params['s11']
    del params['s12']
    del params['s21']
    del params['s22']
    del params['random_injection_parameters']
    result.plot_corner(lionize=settings.other_settings.lionize, parameters=params)

    time_and_phase_shifted_result = adjust_phase_and_geocent_time_complete_posterior_proper(result=result, ifo=ifos[0],
                                                                                            verbose=True)
    time_and_phase_shifted_result.label = 'time_and_phase_shifted'
    time_and_phase_shifted_result.save_to_file()
    time_and_phase_shifted_result.plot_corner(parameters=params)

    priors = settings.recovery_priors.proper_dict()

    waveform_generator_memory = bilby.gw.WaveformGenerator(
        time_domain_source_model=time_domain_nr_hyb_sur_waveform_with_memory_wrapped,
        parameters=settings.injection_parameters.__dict__,
        waveform_arguments=settings.waveform_arguments.__dict__,
        **settings.waveform_data.__dict__)

    waveform_generator_no_memory = bilby.gw.WaveformGenerator(
        time_domain_source_model=time_domain_nr_hyb_sur_waveform_without_memory_wrapped,
        parameters=settings.injection_parameters.__dict__,
        waveform_arguments=settings.waveform_arguments.__dict__,
        **settings.waveform_data.__dict__)

    likelihood_memory = bilby.gw.likelihood \
        .GravitationalWaveTransient(interferometers=ifos,
                                    waveform_generator=waveform_generator_memory,
                                    priors=priors,
                                    time_marginalization=settings.other_settings.time_marginalization,
                                    distance_marginalization=settings.other_settings.distance_marginalization,
                                    phase_marginalization=settings.other_settings.phase_marginalization)

    likelihood_no_memory = bilby.gw.likelihood \
        .GravitationalWaveTransient(interferometers=ifos,
                                    waveform_generator=waveform_generator_no_memory,
                                    priors=priors,
                                    time_marginalization=settings.other_settings.time_marginalization,
                                    distance_marginalization=settings.other_settings.distance_marginalization,
                                    phase_marginalization=settings.other_settings.phase_marginalization)

    reweighed_log_bf = reweigh_by_two_likelihoods(posterior=time_and_phase_shifted_result.posterior,
                                                  likelihood_memory=likelihood_memory,
                                                  likelihood_no_memory=likelihood_no_memory)

    debug_evidence, debug_weights = reweigh_by_likelihood(likelihood_no_memory, time_and_phase_shifted_result)
    logger.info("NR Sur LOG BF: " + str(debug_evidence - time_and_phase_shifted_result.log_evidence))
    logger.info("MEMORY LOG BF: " + str(reweighed_log_bf))

    try:
        time_and_phase_shifted_result.plot_corner(label='reweighed', weights=debug_weights)
    except Exception:
        pass

    return time_and_phase_shifted_result

