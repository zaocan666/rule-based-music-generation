#_*_coding:utf-8_*_
from mingus.core import notes, chords 
from mingus.containers import * 
import mingus.midi.pyfluidsynth as fluidsynth

class Music_play():
    def __init__(self, time_per_duration):
        
        self.time_per_duration = time_per_duration
        self.synth = fluidsynth.Synth(1)
        self.synth.start(driver="alsa")

        # soundFont = synth.sfload("/home/pi/Documents/ChoriumRevA.SF2")
        soundFont = self.synth.sfload("/home/pi/music_pro/arachno-soundfont-10-sf2/Arachno SoundFont - Version 1.0.sf2")

        # 设置乐器的channel，最后两个参数是bank和preset数
        self.synth.program_select(1, soundFont, 0, 0) #Grand piano
        self.synth.program_select(2, soundFont, 0, 41) #Violin
        self.synth.program_select(3, soundFont, 0, 42) #Cello
        self.synth.program_select(4, soundFont, 0, 46) #Orchestral Harp
        self.synth.program_select(5, soundFont, 0, 56) #Trumpet
        self.synth.program_select(6, soundFont, 0, 32) #Acoustic Bass
        self.synth.program_select(7, soundFont, 0, 10) #Music Box
        self.synth.program_select(8, soundFont, 0, 16) #DrawBar Organ
        self.synth.program_select(9, soundFont, 0, 24) #Nylon Guitar        
        #self.synth.program_select(10, soundFont, 0, 54) #Synth Voice
        #self.synth.program_select(11, soundFont, 0, 52) #Choir Aahs
        #self.synth.program_select(12, soundFont, 0, 48) #Strings Ensemble 1
        #self.synth.program_select(13, soundFont, 0, 55) #Orchestra Hit
        self.channels_num = 9

        self.onNotes = []
    
    def start_nodes(self, channel, notes, sustain):
        self.note_on(notes, channel)
        self.onNotes.append({'channel':channel, 'notes':notes, 'left_time':self.time_per_duration/float(sustain)})

    def time_update(self, time_interval):
        i=0
        while i<len(self.onNotes):
            self.onNotes[i]['left_time'] -= time_interval
            if self.onNotes[i]['left_time'] < time_interval*0.5:
                self.note_off(self.onNotes[i]['notes'], self.onNotes[i]['channel'])
                self.onNotes.pop(i)
            else:
                i=i+1

    def parse_note_name(self, note):
        return note[:-1] + '-' + note[-1]

    def note_on(self, notes, channel):
        for note in notes:
            if note=='r':
                continue
            
            note_num = int(Note(self.parse_note_name(note)))
            self.synth.noteon(channel, note_num, 90)
    
    def note_off(self, notes, channel):
        for note in notes:
            if note=='r':
                continue
            
            note_num = int(Note(self.parse_note_name(note)))
            self.synth.noteoff(channel, note_num)
    
    def stop_all_notes(self):
        i=0
        while i<len(self.onNotes):
            self.note_off(self.onNotes[i]['notes'], self.onNotes[i]['channel'])
            i = i+1
        self.onNotes = []