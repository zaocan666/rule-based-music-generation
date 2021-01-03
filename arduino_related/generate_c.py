from pychord import Chord

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

output_str = ""
for k,v in scales_chords.items():
    output_str += "{"
    for chord in v:
        notes = Chord(chord).components()
        notes_part = notes[:3]
        str_chord = "{\"%s\", \"%s\", \"%s\"}, "%(notes_part[0], notes_part[1], notes_part[2])
        output_str += str_chord
    output_str = output_str[:-2]
    output_str += "}, //%s\n"%k

with open("c.txt", "w") as f:
    f.write(output_str)