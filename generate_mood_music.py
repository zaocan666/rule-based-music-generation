from pychord import Chord
import random
import pretty_midi
import re
import numpy as np

bars_num = 16
tempo = 120

def get_key_from_mood(mood):
    mood_key = {
        5: 'A major',
        4: 'G major',
        3: 'Eb major',
        2: 'D major',
        1: 'E major',
        0: 'C major',
        -1: 'C minor',
        -2: 'D minor',
        -3: 'G minor',
        -4: 'F minor',
    }

    return mood_key[mood]

# 每种scale对应若干chord
def get_scale_chords(scale):
    scales_chords = {
        'A major': [ 'Amaj7', 'Bm7', 'C#m7', 'Dmaj7', 'E7', 'F#m7', 'G#m7b5' ],
        'G major': [ 'Gmaj7', 'Am7', 'Bm7', 'Cmaj7', 'D7', 'Em7', 'F#m7b5' ],
        'Eb major': [ 'Ebmaj7', 'Fm7', 'Gm7', 'Abmaj7', 'Bb7', 'Cm7', 'Dm7b5' ],
        'D major': [ 'Dmaj7', 'Em7', 'F#m7', 'Gmaj7', 'A7', 'Bm7', 'C#m7b5' ],
        'E major': [ 'Emaj7', 'F#m7', 'G#m7', 'Amaj7', 'B7', 'C#m7', 'D#m7b5'],
        'C major': [ 'Cmaj7', 'Dm7', 'Em7', 'Fmaj7', 'G7', 'Am7', 'Bm7b5' ],
        'C minor': [ 'Cm7', 'Dm7b5', 'Ebmaj7', 'Fm7', 'Gm7', 'Abmaj7', 'Bb7' ],
        'D minor': [ 'Dm7', 'Em7b5', 'Fmaj7', 'Gm7', 'Am7', 'Bbmaj7', 'C7' ],
        'G minor': [ 'Gm7', 'Am7b5', 'Bbmaj7', 'Cm7', 'Dm7', 'Ebmaj7', 'F7' ],
        'F minor': [ 'Fm7', 'Gm7b5', 'Abmaj7', 'Bbm7', 'Cm7', 'Dbmaj7', 'Eb7' ]
    }

    return scales_chords[scale]

# progression 依次提取chords中的一个chord，将其转化为音符
def get_notes_from_progression(progression, chords):
    chord_notes = []
    for p in progression:
        chord = chords[p-1]
        notes = Chord(chord).components()
        notes_part = notes[:3]
        chord_notes.append(notes_part)

    return chord_notes

def notes_name2notes(notes_name, octaves):
    notes = []
    for octave in octaves:
        notes += [n+str(octave) for n in notes_name]
    return notes

def create_chord_progression(chord_notes, note_octave, Arousal, Arousal_range):
    chord_progression = []

    chord_duration_idx = round(linear_map(Arousal, Arousal_range[0], Arousal_range[1], 0, 2)) #较低的arousal对应较长duration
    chord_duration = [1,2,4][chord_duration_idx] #指数关系，可能值为1,2,4

    chord_indexes = [] # 每个四分音符上，所用和弦的序号
    for bar in range(bars_num):
        chord_idx = bar%len(chord_notes)
        notes_name = chord_notes[chord_idx]

        first_half = int(bar<bars_num/2) #和弦在后半段整体升八度
        notes = notes_name2notes(notes_name, octaves=[note_octave[0]-first_half])

        for _ in range(chord_duration):
            chord_progression.append({ 'note': notes, 'duration': chord_duration, 'sustain': chord_duration})

        chord_indexes += ([chord_idx]*4)

    return chord_progression, chord_indexes

def near_probability(candidates, last_x):
    start_index = candidates.index(last_x)
    i = 0
    prob = [0]*len(candidates)
    while True:
        if start_index-i>=0:
            prob[start_index-i]=len(candidates)-i
        if start_index+i<len(candidates):
            prob[start_index+i]=len(candidates)-i
        if start_index-i<0 and start_index+i>=len(candidates):
            break
        i += 1

    sum_prob = sum(prob)
    output = [p/float(sum_prob) for p in prob]
    return output

def create_melody(chord_notes, chord_indexes, note_octave):
    melody = []
    last_duration = 4
    duration_choices = [2,4,8]
    melody.append({ 'note': "r", 'duration': 1/4, 'sustain': 1/4}) #前四小节只有和弦
    for bar in range(4, bars_num):

        bar_left = 1
        while bar_left>0:
            chord_idx_idx = int((1-bar_left)*4) # 在当前小节内，时间属于哪个四分音符，[0,1,2,3]
            chord_i = chord_indexes[bar*4+chord_idx_idx]
            notes_name = chord_notes[chord_i]
            notes = notes_name2notes(notes_name, note_octave) #C4 E4 F4 C5 E5 F5

            # duration = random.sample([2,4,8,16], 1)[0]

            duration_prob = near_probability(duration_choices, last_x=last_duration)
            duration = np.random.choice(duration_choices, p=duration_prob)
            last_duration = duration
            # sustain = random.sample([duration, duration//2], 1)[0]
            sustain = duration
            note_probability = [0.8/len(notes)]*len(notes)+[0.2]
            # note = random.sample(notes+['r'], 1)[0]
            note = np.random.choice(notes+['r'], p=note_probability)

            if bar_left-1/duration<0:
                break

            melody.append({'note':[note], 'duration': duration, 'sustain': sustain})

            bar_left -= 1/duration

        melody.append({'note':['r'], 'duration': 1/bar_left, 'sustain': 1/bar_left})

    return melody

def create_arpeggio(chord_notes, chord_indexes, note_octave, arpeggios):
    melody = []

    melody.append({ 'note': "r", 'duration': 1/4, 'sustain': 1/4}) #前四小节只有和弦
    for bar in range(4, bars_num):
        bar_left = 1
        for a in arpeggios:
            durationMatch = re.search('\d+n', a)
            if not durationMatch:
                raise Exception("No duration in arpeggio notation: " + a)
            duration = int(durationMatch[0][:-1])
            # velocityMatch = re.search('\d+(.\d+)?v', a)
            # velocity = float(velocityMatch[0]) if velocityMatch  else None
            sustainMatch = re.search('\d+s', a)
            sustain = int(sustainMatch[0][:-1]) if sustainMatch else duration; 
            positionsMatch = re.search('[\d,r]+$', a)
            if not positionsMatch:
                raise Exception("No positions in arpeggio notation: " + a)
            positionsString = positionsMatch[0]

            if (positionsString == "r"):
                melody.append({ 'note': "r", 'duration': duration, 'sustain': duration})
                continue
            
            chord_idx_idx = int((1-bar_left)*4)
            chord_i = chord_indexes[bar*4+chord_idx_idx]
            notes_name = chord_notes[chord_i]
            notes = notes_name2notes(notes_name, note_octave)

            note_indexes = positionsString.split(',')
            note_list = [notes[int(i_note)-1] for i_note in note_indexes]
            melody.append({ 'note': note_list, 'duration': duration, 'sustain': sustain})
            bar_left -= 1/duration

    return melody

def parse_notes2instrument(melody, instrument, velocity=100):
    time = 0
    for note_info in melody:
        duration = note_info['duration']
        notes = note_info['note']
        sustain = note_info['sustain']

        end_time = time + 1/sustain*time_per_duration
        for note in notes:
            if note=='r':
                continue
            note_number = pretty_midi.note_name_to_number(note)-12
            note = pretty_midi.Note(velocity=velocity, pitch=note_number, start=time, end=end_time)
            instrument.notes.append(note)

        time += 1/duration*time_per_duration

    return instrument

def notes2music(melody, chord_progression=None, output_name = 'output/output.mid'):
    music_output = pretty_midi.PrettyMIDI(initial_tempo=tempo)
    piano_program = pretty_midi.instrument_name_to_program('Electric Grand Piano')
    melody_instrument_name = random.choice(['Violin', 'Cello', 'Electric Grand Piano', 'Orchestral Harp', 'Trumpet'])
    melody_instrument_program = pretty_midi.instrument_name_to_program(melody_instrument_name)

    melody_instrument = pretty_midi.Instrument(program=melody_instrument_program)
    piano = parse_notes2instrument(melody, melody_instrument, velocity=100)
    music_output.instruments.append(piano)

    if chord_progression:
        chord_instrument = pretty_midi.Instrument(program=piano_program)
        chord_instrument = parse_notes2instrument(chord_progression, chord_instrument, velocity=100)
        music_output.instruments.append(chord_instrument)    
    
    # Write out the MIDI data
    music_output.write(output_name)

def notes2txt(melody, settings, output_name = 'output/output.txt'):
    with open(output_name, 'w') as f:
        if settings:
            f.write(str(settings) + '\n')
        for note_info in melody:
            f.write(str(note_info) + '\n')

def linear_map(x, in_min, in_max, out_min, out_max):
    return (x-in_min)/(in_max-in_min)*(out_max-out_min)+out_min

def get_basic_setting(Valence, Arousal, Valence_range, Arousal_range):
    octave = round(linear_map(Valence, Valence_range[0], Valence_range[1], 4, 6))
    # time_per_duration = linear_map(Arousal, Arousal_range[0], Arousal_range[1], 4, 2)
    time_per_duration = 2

    note_octave = [octave, octave+1]

    progressions = [[1, 5, 6, 5],
                    [6, 4, 1, 5],
                    [1, 4, 6, 5],
                    [1, 6, 4, 5]]
    progression = random.sample(progressions, 1)[0]
    # progression = progressions[0]

    arpeggioses =[["2n1s1,2,3", "8n2", "8n3", "8n2", "8n1"],
                ["2n1s1,2,3", "8n2", "8n3", "8n2", "8n1"],
                ["8n4s1", "8n2", "8n4s3", "8n1", "8n4s2", "8n3", "8n4s2", "8n1"],
                ["2n1s1,2,3", "4nr", "4n3"],
                ["8n2s1", "8n2s2", "8n2s1", "8n2s3", "8n2s2", "8n2s3", "8n2s2", "8n2s1"]]
    arpeggios = random.sample(arpeggioses, 1)[0]
    # arpeggios = arpeggioses[2]

    return progression, note_octave, arpeggios, time_per_duration

if __name__ == '__main__':
    # random.seed(1) #确定随机种子

    Valence_range = [-4, 4]
    Arousal_range = [-4, 4]

    # for i in range(Valence_range[0], Valence_range[1]+1):
    i=0
    Valence = 4 # 情绪积极或消极
    Arousal = Valence # 情绪强度

    # 基本的音乐参数
    progression, note_octave, arpeggios, time_per_duration = get_basic_setting(Valence, Arousal, Valence_range, Arousal_range)

    chords = get_scale_chords(get_key_from_mood(Valence))
    chord_notes = get_notes_from_progression(progression, chords) #[len(progression), 3]
    
    # 和弦进行
    chord_progression, chord_indexes = create_chord_progression(chord_notes, note_octave, Arousal, Arousal_range) 
    
    # 旋律
    melody = create_melody(chord_notes, chord_indexes, note_octave)
    # melody = create_arpeggio(chord_notes, chord_indexes, note_octave, arpeggios)

    settings = {'progression':progression, 'note_octave':note_octave, 'arpeggios':arpeggios, 'time_per_duration':time_per_duration}
    notes2txt(chord_progression, settings=settings, output_name='output/output_%d_progression.txt'%(i))
    notes2txt(melody, settings=None, output_name='output/output_%d_melody.txt'%(i))
    notes2music(melody, chord_progression, output_name='output/output_%d.mid'%(i))
    print()