"""
Read files from ./files and extract values from them.
Write one file with all values separated by commas.

Example:
    Input:

    file_1.txt (content: "23")
    file_2.txt (content: "78")
    file_3.txt (content: "3")

    Output:

    result.txt(content: "23, 78, 3")
"""
import os

BASEPATH = ('files/')
def read_files():
    try:
        num_list = []
        for filename in os.listdir(BASEPATH):
            with open(f'{BASEPATH}{filename}', 'r') as f:
                num = f.read().rstrip()
                num_list.append(num)
        result_string = ', '.join([item for item in num_list])
        with open('result.txt', 'w') as fr:
            fr.write(f'{result_string}')
    except Exception as e:
        print(str(e))

read_files()