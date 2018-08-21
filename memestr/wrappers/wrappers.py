import numpy as np
import tupak


def run_basic_injection(injection_model, recovery_model, outdir, **kwargs):
    default_injection_parameters = dict(
        mass_ratio=1.5,
        total_mass=6,
        s11=0,
        s12=0,
        s13=0,
        s21=0,
        s22=0,
        s23=0,
        luminosity_distance=50.,
        inc=np.pi / 2,
        phase=0,
        ra=1.54,
        dec=-0.7,
        psi=2.659,
        geocent_time=1126259642.413,
        )

    default_waveform_arguments = dict(
        LMax=2
    )

    default_waveform_data = dict(
        start_time=0,
        duration=3,
        sampling_frequency=4096,
    )

    default_sampler_kwargs = dict(
        sampler='pymultinest',
        npoints=6000,
        label='IMRPhenomD'
    )

    default_other_kwargs = dict(
        new_seed=True,
        zero_noise=False,
        lionize=True
    )

    if not default_injection_parameters['new_seed']:
        np.random.seed(88170235)

    tupak.core.utils.setup_logger(outdir=outdir, label=default_injection_parameters['label'])

    waveform_arguments = update_kwargs(default_waveform_arguments, kwargs)
    injection_parameters = update_kwargs(default_injection_parameters, kwargs)
    waveform_data = update_kwargs(default_waveform_data, kwargs)
    sampler_kwargs = update_kwargs(default_sampler_kwargs, kwargs)
    other_kwargs = update_kwargs(default_other_kwargs, kwargs)

    for key in waveform_arguments:
        injection_parameters[key] = waveform_arguments[key]

    waveform_generator = tupak.gw.WaveformGenerator(time_domain_source_model=injection_model,
                                                    parameters=injection_parameters,
                                                    waveform_arguments=waveform_arguments,
                                                    **waveform_data)

    ifos = [tupak.gw.detector.get_interferometer_with_fake_noise_and_injection(
        name,
        injection_polarizations=waveform_generator.frequency_domain_strain(),
        injection_parameters=injection_parameters,
        outdir=outdir,
        zero_noise=other_kwargs['zero_noise'],
        **waveform_data) for name in ['H1', 'L1', 'V1']]

    waveform_generator.time_domain_source_model = recovery_model
    priors = dict()

    for key in ['total_mass', 'mass_ratio', 's11', 's12', 's13', 's21', 's22', 's23', 'luminosity_distance',
                'inc', 'phase', 'ra', 'dec', 'geocent_time', 'psi']:
        priors[key] = injection_parameters[key]
    priors['total_mass'] = tupak.core.prior.Uniform(minimum=50, maximum=70, latex_label="$M_{tot}$")
    priors['mass_ratio'] = tupak.core.prior.Uniform(minimum=1, maximum=2, latex_label="$q$")
    priors['luminosity_distance'] = tupak.gw.prior.UniformComovingVolume(name='luminosity_distance', minimum=1e1,
                                                                         maximum=5e3, latex_label="$L_D$")
    priors['inc'] = tupak.core.prior.Uniform(minimum=0, maximum=np.pi, latex_label="$\iota$")
    priors['phase'] = tupak.core.prior.Uniform(name='phase', minimum=0, maximum=2 * np.pi, latex_label="$\phi$")
    priors['ra'] = tupak.core.prior.Uniform(name='ra', minimum=0, maximum=2 * np.pi, latex_label="$RA$")
    priors['dec'] = tupak.core.prior.Cosine(name='dec', latex_label="$DEC$")
    priors['psi'] = tupak.core.prior.Uniform(name='psi', minimum=0, maximum=2 * np.pi, latex_label="$\psi$")
    priors['geocent_time'] = tupak.core.prior.Uniform(1126259642.322, 1126259642.522, name='geocent_time')
    likelihood = tupak.gw.likelihood.GravitationalWaveTransient(interferometers=ifos,
                                                                waveform_generator=waveform_generator,
                                                                prior=priors)

    result = tupak.core.sampler.run_sampler(likelihood=likelihood,
                                            priors=priors,
                                            injection_parameters=injection_parameters,
                                            outdir=outdir,
                                            **sampler_kwargs)
    result.plot_corner(lionize=other_kwargs['lionize'])
    print(result)


def update_kwargs(default_kwargs, kwargs):
    new_kwargs = default_kwargs.copy()
    for key in list(set(default_kwargs.keys()).union(kwargs.keys())):
        new_kwargs[key] = kwargs[key]
    return new_kwargs


def run_basic_injection_NRSur(injection_model, recovery_model, outdir):
    start_time = -0.5
    end_time = 0.01  # 0.029
    duration = end_time - start_time
    run_basic_injection(injection_model=injection_model, recovery_model=recovery_model, outdir=outdir,
                        start_time=start_time, duration=duration, label='NRSur', new_seed=False, zero_noise=True)


def run_basic_injection_imr_phenom(injection_model, recovery_model, outdir):
    run_basic_injection(injection_model=injection_model, recovery_model=recovery_model, outdir=outdir,
                        label='IMRPhenomD', new_seed=True, zero_noise=True)