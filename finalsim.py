import sys
import numpy as np
from scipy import signal
import wcslib as wcs
import matplotlib.pyplot as plt



def main():
    # Parameters
    channel_id = 13
    fc = 3600 #den ska centreras i vår range
    Tb = 215/ fc            # Symbol width in seconds    
    fs = 20000              # Sampling frequency in Hz (>14 400)
    NyQ = fs/2
    Ts = 1/fs
    wp = [3550, 3650]
    ws = [3525, 3750]
    Ap = 1
    As = 60
    Ac = 1.99762975297
    wc = 3600 * 2 * np.pi
    #wp_low = 3650
    #ws_low = 3750
    wp_low = 50 #(hälften av vårat band), för den är centrerad runt 0
    ws_low = 150 #dubbla frekvenserna tas bort. Dubbla frekvens-komponenterna börjar här (2 * (3550 till 3650))
    #ws_low = 3550 * 2 #(My)
    Ap_low = 1
    As_low = 60


    # Detect input or set defaults
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
    

    extra_symbol = [0,1,1,0,0,0,0,1] #lägger till en extra a symbol
    bs = np.concatenate((bs, extra_symbol))

    a1 = wcs.decode_string(bs)
    print('After adding extra symbol:', a1)



    # --------------- TRANSMITTER ---------------

    # Encode baseband signal
    xb = wcs.encode_baseband_signal(bs, Tb, fs)

    # Modulation

    t = np.arange(0, len(xb) * Ts, Ts)

    def xc(t):
        return Ac*np.sin(wc*t)
    
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
    # b, a = signal.iirdesign(wp/Ny, ws/Ny, Ap, As, analog=False, ftype='ellip', output='ba', fs=fs)  
    xt = signal.lfilter(b, a, xm)


    # ----------------- RECEIVER -----------------

    # Channel simulation
    yr = wcs.simulate_channel(xt, fs, channel_id)

    # Band limiter
    ym = signal.lfilter(b, a, yr)

    # Demodulation
    t2 = np.arange(0, len(ym) * Ts, Ts)
    #reshape t2?????

    size_ym = np.size(ym)
    t2 = t2[:size_ym]

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
    #br = br[:-1]
    # Print received bit sequence before and after removal
    d1 = wcs.decode_string(br)
    print('Before removing last symbol:', d1)
    print('Before removing last symvbol (bit):', br)
    #br = br[:-7]  # Remove the last symbol

    data_rx = wcs.decode_string(br)
    data_rx = data_rx[:-1]
    print('Received: ' + data_rx)
    print('Received (bit):', br)

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
