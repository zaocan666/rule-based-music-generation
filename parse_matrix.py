import numpy as np
from numpy.core.fromnumeric import shape

def normalize(matrix, min, max):
    return (matrix-min)/(max-min)

def conv2d(x, operator):
    assert operator.shape[0]==3 and operator.shape[1]==3
    x_padding = np.zeros(shape=[x.shape[0]+2, x.shape[1]+2])
    x_padding[1:-1, 1:-1] = x
    result = np.zeros(x.shape)
    for i in range(x.shape[0]):
        for j in range(x.shape[1]):
            result_ij = 0
            for o_i in range(operator.shape[0]):
                for o_j in range(operator.shape[1]):
                    result_ij += operator[o_i][o_j]*x_padding[i+o_i][j+o_j]
            result[i][j] = result_ij
    
    return result

def get_mean_Laplace(matrix):
    laplace_operator = np.array([[1, 1, 1],
                        [1, -8, 1],
                        [1, 1, 1]])
    
    laplace_result = conv2d(matrix, laplace_operator)
    return laplace_result.mean()

def matrix_circle_list(matrix):
    assert matrix.shape[0]>1 and matrix.shape[1]>1

    output_list = []
    row = matrix.shape[0]
    col = matrix.shape[1]
    all_count = row*col
    i=0
    j=0
    while len(output_list)<all_count:
        # 最上面一行
        for _ in range(col-1):
            output_list.append(matrix[i][j])
            j += 1

        # 最右边一列
        for _ in range(row-1):
            output_list.append(matrix[i][j])
            i += 1
        # 最下面一行
        for _ in range(col-1):
            output_list.append(matrix[i][j])
            j -= 1
        # 最左边一列
        for _ in range(row-1):
            output_list.append(matrix[i][j])
            i -= 1
        
        i += 1
        j += 1
        row -= 2
        col -= 2

        if row==1:
            for _ in range(col):
                output_list.append(matrix[i][j])
                j += 1
        elif col==1:
            for _ in range(row):
                output_list.append(matrix[i][j])
                i += 1

    return output_list

def get_matrix_feature(matrix, martix_min, martix_max):
    matrix_normalized = normalize(matrix, martix_min, martix_max)
    laplace_mean = get_mean_Laplace(matrix_normalized)
    all_laplace_min = -2.0595
    all_laplace_max = 0

    matrix_list = matrix_circle_list(matrix_normalized)
    return [laplace_mean, all_laplace_min, all_laplace_max], matrix_list

def test_max_min():
    data = []
    for i in range(int(1e5)):
        matrix_normalized = normalize(np.random.rand(5, 4), 0, 1)
        laplace_mean = get_mean_Laplace(matrix_normalized)
        data.append(laplace_mean)
    
    import matplotlib.pyplot as plt
    plt.hist(data, bins=40, density=True, facecolor="blue", edgecolor="black", alpha=0.7)
    plt.show()
    print(np.array(data).min())
    print(np.array(data).max())
    print()

if __name__=='__main__':
    test_matrix = np.random.rand(5, 4)

    get_matrix_feature(test_matrix, 0, 1)
    # test_max_min()