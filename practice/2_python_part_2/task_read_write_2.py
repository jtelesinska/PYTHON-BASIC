"""
Use function 'generate_words' to generate random words.
Write them to a new file encoded in UTF-8. Separator - '\n'.
Write second file encoded in CP1252, reverse words order. Separator - ','.

Example:
    Input: ['abc', 'def', 'xyz']

    Output:
        file1.txt (content: "abc\ndef\nxyz", encoding: UTF-8)
        file2.txt (content: "xyz,def,abc", encoding: CP1252)
"""


def generate_words(n=20):
    import string
    import random

    words = list()
    for _ in range(n):
        word = ''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 10)))
        words.append(word)

    return words

def write_files(words):
    try:
        with open("file1.txt", "w", encoding='utf-8') as file1, open("file2.txt", "w", encoding="cp1252") as file2:
            file1.write("\n".join(words))
            file2.write(",".join(words[::-1]))
    except Exception as e:
        print(str(e))


if __name__ == "__main__":
    words = generate_words()
    write_files(words)
