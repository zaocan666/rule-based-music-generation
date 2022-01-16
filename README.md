# rule-based-music-generation
从矩阵生成规则性的音乐
尝试了在arduino、stm32上的部署，最终用在了树莓派上（raspberry文件夹）

## 矩阵解析 parse_matrix.py
先将矩阵标准化（化到0~1区间），计算矩阵的两个特征
- laplace_mean：对矩阵进行laplace卷积（same padding），求结果的平均值的绝对值。此外，用随机矩阵生成的方法统计laplace_mean可能的最大最小值。
- matrix_list：用回环遍历的方法得到矩阵的list

## 音乐特征 generate_mood_music.py
- Valence：将矩阵的laplace_mean用sqrt_map映射为Valence，表示音乐的情绪
- progression：和弦进行序列，随机选择一种，如[1, 5, 6, 5]
- note_octave：音高，生成的音符在哪个八度，从Valence映射

## 音乐生成 generate_mood_music.py
生成的音乐包括chord_progression和melody两部分，共16小节，chord_progression用钢琴演奏，melody随机选择一种乐器
### chord_progression：
- 和弦音符：由Valence映射选择一个key（调式），得到key的所有三和弦，根据progression取出其中四个三和弦。
- duration：由Valence映射得到，从\[1,2,4\]中选择一个（低Valence对应长音程），结果是一个小节中将同一和弦重复1/2/4次。
- octave：前八个小节和弦每个音符的音高是note_octave\[0\]-1，后八个小节整体升八度，即note_octave\[0\]。

四组和弦交替演奏，一个小节中只演奏一组和弦，所以16个小节四组和弦演奏四次。

### melody：
melody由一连串音符组成，前后两个音符之间不重叠，音符的选择由矩阵特征matrix_list的元素决定。

- 音符：是当前小节chord_progression的音符，有三个
- 音高：note_octave\[0\]和note_octave\[1\]
- 选择音符音高：音符音高的组合提供了六种选择，依据矩阵特征matrix_list的当前元素映射为0到5，选择其一。
- 休止符：每次生成音符有20%的可能产生休止符。
- duration：从\[2,4,8\]中随机选择，不过选择概率与前一音符的duration有关，与前一duration越接近，选择概率越高。
- 小节取整：每小节的最后一个音符可能会超出本小节，为了音乐的和谐，我们将这样的音符置为休止符。


## 遇到的问题
- 对矩阵进行laplace卷积时，最开始使用的是zero padding，后来发现这种方法会使全零矩阵的laplace_mean为零，但使全1矩阵的laplace_mean很小，违背初衷，两种矩阵都很平缓，laplace_mean应该都为0才对。于是改用same padding
- melody中音符的duration随机生成，可能会出现某音符越出本小节到下一小节的情况，我们将这样的音符换为休止符。但最开始因为往了添加休止符，出现bug，后来才发现这个错误。

## Reference
https://github.com/epranka/soundcode
