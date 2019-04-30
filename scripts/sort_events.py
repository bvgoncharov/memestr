import bilby as bb
import numpy as np
import pandas as pd

snrs = pd.DataFrame(['id', 'snr'])

for i in range(5):
    ifos = bb.gw.detector.InterferometerList.from_hdf5('parameter_sets/' + str(i) + '_H1L1V1.h5')
    best_snrs = [ifo.meta_data['matched_filter_SNR'].real for ifo in ifos]
    network_snr = np.sqrt(np.sum([snr ** 2 for snr in best_snrs]))
    snrs.append(dict(id=i, snr=network_snr))

print(snrs)