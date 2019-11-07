from __future__ import division

import os
import memestr
import bilby
import configargparse

p = configargparse.ArgParser()
p.add_argument('--outdir', type=str, required=True)
p.add_argument('--sub_run_id', type=int)
p.add_argument('--routine', type=str, required=True)
p.add_argument('--reweight_model', type=str)
p.add_argument('--recovery_model', type=str)

p.add_argument('--distance_marginalization', type=bool, default=False)
p.add_argument('--time_marginalization', type=bool, default=False)
p.add_argument('--phase_marginalization', type=bool, default=False)
p.add_argument('--random_seed', type=float, default=42)
p.add_argument('--lionize', type=bool, default=False)

p.add_argument('--duration', type=float, default=16)
p.add_argument('--sampling_frequency', type=float, default=2048)
p.add_argument('--start_time', type=float, default=0)

p.add_argument('--alpha', type=float, default=0.1)
p.add_argument('--minimum_frequency', type=float, default=20)

p.add_argument('--label', type=str, default='IMRPhenomD')
p.add_argument('--sampler', type=str, default='dynesty')
p.add_argument('--npoints', type=float, default=200)
p.add_argument('--walks', type=float, default=50)
p.add_argument('--dlogz', type=float, default=0.1)
p.add_argument('--resume', type=bool, default=False)
p.add_argument('--clean', type=bool, default=False)
p.add_argument('--plot', type=bool, default=False)

p.add_argument('--zero_noise', type=bool, default=False)
p.add_argument('--detectors', type=list, default=['H1', 'L1', 'V1'])

priors = bilby.gw.prior.BBHPriorDict()
priors.from_file('bbh.prior')

options = p.parse_args().__dict__
options['priors'] = priors

bilby.core.utils.logger.info(options['recovery_model'])

bilby.core.utils.logger.info(memestr.core.waveforms.models.get(options.get('recovery_model'), ''), None)

print(options.get('recovery_model'))
print(options.get('reweight_model'))
options['recovery_model'] = memestr.core.waveforms.models.get(options.get('recovery_model', ''), None)
options['reweight_model'] = memestr.core.waveforms.models.get(options.get('reweight_model', ''), None)

dir_path = os.path.dirname(os.path.realpath(__file__))
routine = memestr.routines[options['routine']]
routine(dir_path=dir_path, **options)




