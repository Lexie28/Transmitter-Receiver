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
    wp_low = 3600
    ws_low = 3750
    Ap_low = 2
    As_low = 40


    # Detect input or set defaults
    #sys.argv = ["-b", "010010000110100100100001"]
    string_data = True
    if len(sys.argv) == 2:
        data = str(sys.argv[1])

    elif len(sys.argv) == 3 and str(sys.argv[1]) == '-b':
        string_data = False
        data = str(sys.argv[2])

    else:
        print('Warning: No input arguments, using defaults.', file=sys.stderr)
        data = "Hello World!"

    # Convert string to bit sequence or string bit sequence to numeric bit
    # sequence
    if string_data:
        bs = wcs.encode_string(data)
    else:
        bs = np.array([bit for bit in map(int, data)])

    print(bs)
    a = wcs.decode_string(bs)
    print('Before adding extra symbol:', a)

    #Add extra symbol

    extra_symbol = [0,1,1,0,0,0,0,1] #lägger till en extra a symbol
    bs = np.concatenate((bs, extra_symbol))

    b = wcs.decode_string(bs)
    print('After adding extra symbol:', b)

    #print(bs)


    # --------------- TRANSMITTER ---------------

    # Encode baseband signal
    xb = wcs.encode_baseband_signal(bs, Tb, fs)

    # Modulation

    t = np.arange(0, len(xb) * Ts, Ts)
    #t = np.arange(0, len(xb) * Ts - Ts, Ts)

    def xc(t):
        return Ac*np.sin(wc*t)

    #t = np.arange(0, len(xb) * Ts, Ts)

    #Resize xc to the size of xb
    xc = xc(t)
    size_xb = np.size(xb)
    xc = xc[:size_xb]
    
    def xm(t):
        xc_t = xc
        print("Length of xc(t):", len(xc_t))
        print("Length of xb:", len(xb))
        return xc_t*xb
    
    xm = xm(t)

    # Band limiter
    b, a = signal.iirdesign(wp, ws, Ap, As, analog=False, ftype='ellip', output='ba', fs=fs)    
    xt = signal.lfilter(b, a, xm)
    #extra_symbols = np.zeros(int(fs*0.1))  # Lägger till en tyst period på 0.1 sekunder
    #xt = np.concatenate((xt, extra_symbols))

    sd.play(xt, fs, blocking=True)


if __name__ == "__main__":
    main()
