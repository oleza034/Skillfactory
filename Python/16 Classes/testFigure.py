from figure import Rectangle, Square, Circle, Triangle

rectangle1 = Rectangle(3, 4)
rectangle2 = Rectangle(12, 5)

print(rectangle1)
print(rectangle2)

square1 = Square(5)
square2 = Square(10)

print(square1)
print(square2)

circle1 = Circle(5)
circle2 = Circle(10)

print(circle1)
print(circle2)

'''
    Triangle(width, height, x, y) is nonsense.
    I assume that triangle has 3 corners:
    (0, 0), (0, width), (x, y)
'''
triangle1 = Triangle(1, 1, 2)
triangle2 = Triangle(5, 10, 50)

print(triangle1)
print(triangle2)

figures = [rectangle1, rectangle2, square1, square2, circle1, circle2, triangle1, triangle2]

print('\nFigures\' area:')
for figure in figures:
    if isinstance(figure, Square):
        print('Square', end='')
    elif isinstance(figure, Circle):
        print('Circle', end='')
    elif isinstance(figure, Rectangle):
        print('Rectangle', end='')
    elif isinstance(figure, Triangle):
        print('Triangle', end='')
    else:
        print('Figure', end='')
    print(' area:', figure.getArea())