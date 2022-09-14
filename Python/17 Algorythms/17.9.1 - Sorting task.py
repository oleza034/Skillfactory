import random

def qsort(array, left=None, right=None, middle=None, debug=False, rnd=False, desc=False):
    '''
    quick sorting array with borders (left, right), with given middle.
    if borders not given, use the whole array
    rnd = use random middle from the array
    desc = sort descessing
    '''
    # define variables
    if left is None:
        left = 0
    if right is None:
        right = len(array) - 1
    if rnd:
        middle = random.choice(array[left:right + 1])
    if middle is None:
        middle = array[(left + right) // 2]
    if debug:
        print('sorting ' + ('sub' if left > 0 or right < len(array) - 1 else '')
              + f'array: {array[left:right + 1]}, middle = {middle}' + (' (random)' if rnd else ''))

    # quick sort around the middle
    p = middle
    i, j = left, right
    while i <= j:
        # passing items in array which are on the right sight of chosen value
        while not desc and array[i] < p or desc and array[i] > p:
            i += 1
        while not desc and array[j] > p or desc and array[j] < p:
            j -= 1
        if i <= j:
            array[i], array[j] = array[j], array[i]
            i += 1
            j -= 1

    if j > left:
        qsort(array, left, j, debug=debug, rnd=rnd, desc=desc)
    if right > i:
        qsort(array, i, right, debug=debug, rnd=rnd, desc=desc)

    return array


s = input('Please enter numbers separated by space: ')
while not all(map(lambda x: x.isdigit(), s.split())):
    s = input('Incorrect input. Please enter numbers separated by space: ')
array = list(map(int, s.split()))

s = input('Please enter the middle number: ')
while not s.isdigit() or all(map(lambda x: x > int(s), array)) or all(map(lambda x: x < int(s), array)):
    s = input('Wrong middle number. Please try again: ')
middle = int(s)

array = qsort(array, middle=middle)

i = 0
while array[i+1] < middle:
    i += 1
j = 11 + sum(map(lambda x: len(str(x)) + 2, array[:i+1]))

print('sorted array:', array)
print(' ' * j, '^')
print('index of element that is less than middle and the next element is greater or equal to middle:', i)
