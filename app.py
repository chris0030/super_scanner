from matplotlib import mlab as mlab
from rtlsdr import RtlSdr
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import time

# Set to true to display graphs of each chunk in browser
# Adds ten second delay per loop for displaying
GRAPH_TO_BROWSER = True

LOWER_SCAN_LIMIT = 30e6
UPPER_SCAN_LIMIT = 1000e6


class Scanner:

    def __init__(self, center_freq):
        self.sdr = RtlSdr()
        self.sdr.sample_rate = 2.048e6
        self.sdr.set_gain = 4
        self.sdr.set_frequency_correction = 60
        self.power_threshold = 10
        self.center_frequency = center_freq

    def get_samples(self):
        # Return ndArray of samples
        return self.sdr.read_samples(1024)

    def return_power_and_freq(self, samples):
        # Returns a power array of power and psd_freq array of frequency
        power, psd_freq = mlab.psd(
            samples,
            NFFT=1024,
            Fs=self.sdr.sample_rate / 1e6
        )
        psd_freq = psd_freq + self.sdr.center_freq/1e6
        return (power, psd_freq)

    def return_freq_above_rate(self, power, psd_freq):
        # Returns an array of frequencies that are above the POWER_THRESHOLD
        indices_above_rate = np.nonzero(power > self.power_threshold)
        return [psd_freq[i] for i in indices_above_rate[0]]

    def increment_center_freq(self):
        # Increments the center frequency by the sample rate (which is the bandwidth)
        self.center_freq += self.sdr.sample_rate


if __name__ == "__main__":
    scanner = Scanner(LOWER_SCAN_LIMIT)
    freq_of_note = []
    while scanner.center_freq < UPPER_SCAN_LIMIT:
        print(f'Scanning {scanner.center_freq/1e6}mhz')
        samples = scanner.get_samples()
        power, psd_freq = scanner.return_power_and_freq(samples)
        if GRAPH_TO_BROWSER:
            fig = go.Figure(
                data=go.Scatter(
                    x=psd_freq,
                    y=power
                ), layout_yaxis_range=[0, 100])
            fig.show()
            time.sleep(10)
        freq_above_rate = scanner.return_freq_above_rate(power, psd_freq)
        if len(freq_above_rate):
            print(f'{len(freq_above_rate)} found')
        freq_of_note += freq_above_rate
        scanner.increment_center_freq()
    scanner.sdr.close()
    scanner.sdr = None
    print(frequencies_of_note)
