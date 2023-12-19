import sys
import numpy as np
from scipy import signal
import wcslib as wcs
import matplotlib.pyplot as plt
import sounddevice as sd



def main():
    # Parameters
    channel_id = 13
    fc = 3600
    Tb = 215/ fc            # Symbol width in seconds    
    fs = 20000              # Sampling frequency in Hz (>14 400)
    Ts = 1/fs
    wp = [3550, 3650]
    ws = [3525, 3750]
    Ap = 1
    As = 60
    Ac = 1.99762975297
    wc = 3600 * 2 * np.pi
    wp_low = 50
    ws_low = 150
    #ws_low = 3550 * 2 #(My)
    Ap_low = 1
    As_low = 60
    K = fs*10 #Just an example with X seconds

    # ----------------- RECEIVER -----------------

    # Channel simulation
    #yr = wcs.simulate_channel(xt, fs, channel_id)
    yr = sd.rec(K, samplerate=fs, channels=1, blocking=True)
    #slicing yr[:,0]
    yr = yr[:,0]

    # Band limiter
    b, a = signal.iirdesign(wp, ws, Ap, As, analog=False, ftype='ellip', output='ba', fs=fs)
    ym = signal.lfilter(b, a, yr)
    print(ym.shape)

    # Demodulation
    t2 = np.arange(0, len(ym) * Ts, Ts)
    yId = ym * np.cos(wc * t2)
    yQd = -ym * np.sin(wc * t2)


    # Low-pass filtering
    b_lp, a_lp = signal.iirdesign(wp_low, ws_low, Ap_low, As_low, analog=False, ftype='ellip', output='ba', fs=fs)

    yIb = signal.lfilter(b_lp, a_lp, yId)
    yQb = signal.lfilter(b_lp, a_lp, yQd)

    ybp = np.arctan2(yQb, yIb)
    ybm = np.sqrt(yIb**2 + yQb**2)


    # Baseband and string decoding
    br = wcs.decode_baseband_signal(ybm, ybp, Tb, fs)
    print(br)
    #br = br[:-1]
    data_rx = wcs.decode_string(br)
    data_rx = data_rx[:-1]
    print('Received: ' + data_rx)

    '''
    fig, ax = plt.subplots()
    ax.plot(t, xm, label="xm")
    ax.set_xlabel('s')
    ax.set_ylabel('xc(t)')
    ax.set_xlim(0, 0.01)        
    #ax.set_ylim(-1, 1)        
    ax.legend()
    ax.grid()'''


if __name__ == "__main__":
    main()
