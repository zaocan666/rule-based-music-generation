import pretty_midi
import random

def parse_notes2instrument(melody, instrument, time_per_duration, velocity=100):
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

def notes2music(time_per_duration, melody=None, chord_progression=None, output_name = 'output.mid'):
    music_output = pretty_midi.PrettyMIDI()
    piano_program = pretty_midi.instrument_name_to_program('Electric Grand Piano')
    melody_instrument_name = random.choice(['Violin', 'Cello', 'Electric Grand Piano', 'Orchestral Harp', 'Trumpet'])
    melody_instrument_program = pretty_midi.instrument_name_to_program(melody_instrument_name)

    if melody:
        melody_instrument = pretty_midi.Instrument(program=melody_instrument_program)
        piano = parse_notes2instrument(melody, melody_instrument, time_per_duration, velocity=100)
        music_output.instruments.append(piano)

    if chord_progression:
        chord_instrument = pretty_midi.Instrument(program=piano_program)
        chord_instrument = parse_notes2instrument(chord_progression, chord_instrument, time_per_duration, velocity=100)
        music_output.instruments.append(chord_instrument)    
    
    # Write out the MIDI data
    music_output.write(output_name)

def dict_from_line(line):
    vs = line.split(' ')
    duration = int(vs[-1])
    notes = vs[:-1]
    return { 'note': notes, 'duration': duration, 'sustain': duration}

def read_from_txt(name):
    with open(name, 'r') as f:
        lines = f.readlines()

    chord_output = []
    i = 0
    while True:
        if "melody" in lines[i]:
            break
        chord_output.append(dict_from_line(lines[i]))
        i += 1
    
    melody_output = []
    i += 1
    while i<len(lines):
        melody_output.append(dict_from_line(lines[i]))
        i += 1

    return chord_output, melody_output

if __name__ == "__main__":
    root = './arduino_related/'
    chord_output, melody_output = read_from_txt(root+'arduino_out.txt')
    notes2music(2, chord_progression=chord_output, melody=melody_output, output_name=root+'output.mid')