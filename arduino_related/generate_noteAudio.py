import matplotlib.pyplot as plt
import math
from scipy.io.wavfile import write
import numpy as np

sample_rate = 44100

def envelope_generate(attack_time, decay_time, sustain_time, release_time, sustain_level):
    output = []

    attack_num = attack_time*sample_rate
    for i in range(int(attack_num)):
        output.append(i/float(attack_num))

    decay_num = decay_time*sample_rate
    for i in range(int(decay_num)):
        output.append(1-(1-sustain_level)*i/float(decay_num))

    sustain_num = sustain_time*sample_rate
    output += ([sustain_level]*int(sustain_num))

    release_num = release_time*sample_rate
    for i in range(int(release_num)):
        output.append(sustain_level*(1-i/float(release_num)))

    return output

def generate_note(freq):
    P3 = 0.6
    P4 = 1000
    P6 = freq
    P7 = 0 
    P8 = 5
    
    envelope = envelope_generate(P3*1/6, P3*1/6, P3*3/6, P3*1/6, 0.75)

    output = []
    for i in range(len(envelope)):
        t = i/len(envelope)*float(P3)
        I = ((P8-P7)*envelope[i]+P7)#*P6*2*math.pi
        # I = 5

        modulation_signal = I*math.sin(2*math.pi*P6*t)
        # modulation_signal = 0
        signal_i = envelope[i]*math.sin(2*math.pi*freq*t+modulation_signal)
        output.append(signal_i)
    
    return output

def get_wave(freq, duration=0.5):
    '''
    Function takes the "frequecy" and "time_duration" for a wave 
    as the input and returns a "numpy array" of values at all points 
    in time
    '''
    
    amplitude = 4096
    t = np.linspace(0, duration, int(sample_rate * duration))
    wave = amplitude * np.sin(2 * np.pi * freq * t)
    
    return wave


if __name__ == "__main__":
    output = generate_note(440)
    # data = get_wave(440)
    data = np.array(output)
    data = data * (16300/np.max(data))
    write('twinkle-twinkle.wav', sample_rate, data.astype(np.int16))
    plt.plot(data)
    plt.show()