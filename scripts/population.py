import logging
import numpy as np
import matplotlib.pyplot as plt
import bilby
from memestr.core.population import mass_pdf, mass_ratio_pdf, primary_mass_pdf
from memestr.core.waveforms import time_domain_IMRPhenomD_waveform_with_memory
from memestr.core.parameters import AllSettings

logger = logging.getLogger('bilby')
logger.disabled = True

pm, pm_pdf = primary_mass_pdf(1000)
mr, mr_pdf = mass_ratio_pdf(1000)


def debug_plots():
    qs, m_1, probs = mass_pdf(size=1000)
    q_mesh, m_mesh = np.meshgrid(qs, m_1)

    cf = plt.contourf(q_mesh, m_mesh, probs)
    plt.xlabel('mass_ratio')
    plt.ylabel('primary mass')
    plt.title('PDF')
    plt.colorbar(cf)
    plt.show()
    plt.clf()

    qs, q_probs = mass_ratio_pdf(size=1000)
    plt.plot(qs, q_probs)
    plt.xlabel('mass_ratio')
    plt.ylabel('Probability')
    plt.title('PDF')
    plt.show()
    plt.clf()

    m_1, m_1_probs = primary_mass_pdf(size=1000)
    plt.plot(m_1, m_1_probs)
    plt.xlabel('primary mass')
    plt.ylabel('Probability')
    plt.title('PDF')
    plt.show()
    plt.clf()


def create_parameter_set(filename):
    best_snr = 0
    settings = AllSettings()
    while best_snr < 8:
        mass_1 = bilby.core.prior.Interped(xx=pm, yy=pm_pdf).sample()
        mass_ratio = bilby.core.prior.Interped(xx=mr, yy=mr_pdf).sample()
        total_mass = mass_1 + mass_1 / mass_ratio
        luminosity_distance = \
            bilby.gw.prior.UniformComovingVolume(name='luminosity_distance', minimum=1e2, maximum=2e3).sample()
        dec = bilby.core.prior.Cosine(name='dec').sample()
        ra = bilby.core.prior.Uniform(name='ra', minimum=0, maximum=2 * np.pi).sample()
        inc = bilby.core.prior.Sine(name='inc').sample()
        psi = bilby.core.prior.Uniform(name='psi', minimum=0, maximum=np.pi).sample()
        phase = bilby.core.prior.Uniform(name='phase', minimum=0, maximum=2 * np.pi).sample()

        s11 = 0.0
        s12 = 0.0
        s13 = 0.0
        s21 = 0.0
        s22 = 0.0
        s23 = 0.0

        settings.injection_parameters.update_args(mass_ratio=mass_ratio, total_mass=total_mass,
                                                  luminosity_distance=luminosity_distance, dec=dec, ra=ra,
                                                  inc=inc, psi=psi, phase=phase, s11=s11, s12=s12, s13=s13,
                                                  s21=s21, s22=s22, s23=s23)
        settings.waveform_data.duration = 16
        waveform_generator = \
            bilby.gw.WaveformGenerator(time_domain_source_model=time_domain_IMRPhenomD_waveform_with_memory,
                                       parameters=settings.injection_parameters.__dict__,
                                       waveform_arguments=settings.waveform_arguments.__dict__,
                                       **settings.waveform_data.__dict__)

        hf_signal = waveform_generator.frequency_domain_strain()
        ifos = [bilby.gw.detector.get_interferometer_with_fake_noise_and_injection(
            name,
            injection_polarizations=hf_signal,
            injection_parameters=settings.injection_parameters.__dict__,
            zero_noise=False,
            plot=False,
            **settings.waveform_data.__dict__) for name in settings.detector_settings.detectors]
        best_snrs = [ifo.meta_data['optimal_SNR'] for ifo in ifos]
        best_snr = max(best_snrs)
        print(best_snr)

    with open('parameter_sets/' + str(filename), 'w') as f:
        f.write('total_mass=' + str(settings.injection_parameters.total_mass) +
                ' mass_ratio=' + str(settings.injection_parameters.mass_ratio) +
                ' luminosity_distance=' + str(settings.injection_parameters.luminosity_distance) +
                ' dec=' + str(settings.injection_parameters.dec) +
                ' ra=' + str(settings.injection_parameters.ra) +
                ' inc=' + str(settings.injection_parameters.inc) +
                ' psi=' + str(settings.injection_parameters.psi) +
                ' phase=' + str(settings.injection_parameters.phase) +
                ' s11=' + str(settings.injection_parameters.s11) +
                ' s12=' + str(settings.injection_parameters.s12) +
                ' s13=' + str(settings.injection_parameters.s13) +
                ' s21=' + str(settings.injection_parameters.s21) +
                ' s22=' + str(settings.injection_parameters.s22) +
                ' s23=' + str(settings.injection_parameters.s23))


for i in range(128):
    create_parameter_set(i)
from memestr.core.submit import get_injection_parameter_set

params = get_injection_parameter_set(id=10)
print(params)