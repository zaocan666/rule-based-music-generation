#_*_coding:utf-8_*_
from music_play import Music_play
import numpy as np
from parse_matrix import get_matrix_feature, matrix_change, normalize
from generate_mood_music import sqrt_map, generate_music_from_Valence, notes2txt #notes2music
from music_play import Music_play
import time

time_per_duration = 2.0
Valence_range = [-4, 5] # 情绪Valence范围

if __name__=='__main__':
    matrix_current = np.random.rand(5, 4)
    #matrix_current = np.ones((5, 4))
    last_matrix_normalized = np.zeros((5, 4))

    minimal_interval = time_per_duration/8.0 #最小为八分音符
    music_play = Music_play(time_per_duration)

    while 1:
        #matrix_current = np.array([
        #     [0.18, 0.87, 0.1, 0.82],
        #     [0.68, 0.38, 0, 0.5],
        #     [0.96, 0.132, 0.87, 0.137],
        #     [0.9781, 0.2, 0.1349, 0.358],
        #     [0.315, 0.648, 0.210, 0.68],
        # ])

        # 将matrix归一化到0到1的范围，min和max是marix每个元素可能得到的最小值和最大值
        matrix_current_normalized = normalize(matrix_current, min=0, max=1)

        # 矩阵发生变换
        if matrix_change(matrix_current_normalized, last_matrix_normalized, threshold=0.1):
            print ('matrix change')
            music_play.stop_all_notes()
            # 解析矩阵特征
            [laplace_mean, all_laplace_min, all_laplace_max], matrix_list = get_matrix_feature(matrix_current_normalized)
            
            # 由矩阵特征laplace_mean得到情绪Valence
            Valence = round(sqrt_map(laplace_mean, all_laplace_min, all_laplace_max , Valence_range[0], Valence_range[1]))
            Valence = max(Valence, Valence_range[0])
            Valence = min(Valence, Valence_range[1])
            print ('Valence:'+str(Valence))
            # 由Valence和matrix_list得到音乐
            chord_progression, melody, settings = generate_music_from_Valence(Valence, Valence_range, matrix_list)            
            
            #将音乐记录为txt
            notes2txt(chord_progression, settings=settings, output_name='/home/pi/music_pro/output/output_%d_progression.txt'%(0))
            notes2txt(melody, settings=None, output_name='/home/pi/music_pro/output/output_%d_melody.txt'%(0))
            # notes2music(melody, time_per_duration, chord_progression, output_name='output/output_%d.mid'%(0))
            
            chord_channel = 1
            melody_channel = np.random.choice(range(1, music_play.channels_num+1), 1)[0]
            #melody_channel = 2

            #下个演奏音符的index
            chord_i = 0
            melody_i = 0

            #多久后开启下个音符
            chord_next_time = 0
            melody_next_time = 0
        
        if chord_next_time < minimal_interval*0.5:
            notes = chord_progression[chord_i]['note']
            sustain = chord_progression[chord_i]['sustain']
            music_play.start_nodes(chord_channel, notes, sustain)
            print ('play notes: '+str(chord_channel)+' '+str(notes)+' sustain:' + str(sustain))

            chord_i = (chord_i+1)%len(chord_progression)
            chord_next_time = float(time_per_duration)/chord_progression[chord_i]['duration']
        
        if melody_next_time < minimal_interval*0.5:
            notes = melody[melody_i]['note']
            sustain = melody[melody_i]['sustain']
            music_play.start_nodes(melody_channel, notes, sustain)
            print ('play notes: '+str(melody_channel)+' '+str(notes)+' sustain:' + str(sustain))

            melody_i = (melody_i+1)%len(melody)
            melody_next_time = float(time_per_duration)/melody[melody_i]['duration']

        # 更新时间
        time.sleep(minimal_interval)
        music_play.time_update(minimal_interval)
        chord_next_time -= minimal_interval
        melody_next_time -= minimal_interval
        last_matrix_normalized = matrix_current_normalized
