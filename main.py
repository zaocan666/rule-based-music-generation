import numpy as np
from parse_matrix import get_matrix_feature
from generate_mood_music import linear_map, generate_music_from_Valence, notes2txt, notes2music

if __name__=='__main__':    
    test_matrix = np.random.rand(5, 4)
    # test_matrix = np.array([
    #     [0, 0, 0.1, 0],
    #     [0, 0, 0, 0.5],
    #     [0, 0, 0, 0],
    #     [0, 0.2, 0, 0],
    #     [0, 0, 0, 0],
    # ])
    [laplace_mean, all_laplace_min, all_laplace_max], matrix_list = get_matrix_feature(test_matrix, martix_min=0, martix_max=1)
    
    Valence_range = [-4, 5]
    time_per_duration = 2
    Valence = round(linear_map(laplace_mean, all_laplace_max, all_laplace_min , Valence_range[0], Valence_range[1]))
    chord_progression, melody, settings = generate_music_from_Valence(Valence, Valence_range, matrix_list)

    notes2txt(chord_progression, settings=settings, output_name='output/output_%d_progression.txt'%(0))
    notes2txt(melody, settings=None, output_name='output/output_%d_melody.txt'%(0))
    notes2music(melody, time_per_duration, chord_progression, output_name='output/output_%d.mid'%(0))