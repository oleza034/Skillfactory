class Rectangle:
    def __init__(self, width, height):
        if width < 0 or height < 0:
            raise NonPositiveDigitException('Unable to create rectangle: width or height is less than 0')
        else:
            self.width = width
            self.height = height

    def getWidth(self):
        return self.width

    def getHeight(self):
        return self.height

    def getArea(self):
        return self.width * self.height

    def __str__(self):
        return f'[Rectangle: width={self.width}, height={self.height}]'

class Square(Rectangle):
    def __init__(self, width):
        if width < 0:
            raise NonPositiveDigitException('Unable to create square: width is less than 0')
        else:
            self.width = width
            self.height = width

    def getArea(self):
        return self.width ** 2

    def __str__(self):
        return f'[Square: width={self.width}]'

class Circle:
    def __init__(self, radius):
        if radius < 0:
            raise NonPositiveDigitException('Unable to create circle: radius is less than 0')
        else:
            self.radius = radius

    def getArea(self):
        return round(3.1416 * (self.radius ** 2), 4)

    def __str__(self):
        return f'[Circle: radius={self.radius}]'

class Triangle:
    '''
    assume that one of the sides is horizontal.
    x, y - coordinates of the peak;
    two others peaks are at (0, 0) and (0, width)
    width = the length of the side opposite to the peak at (x, y) coordinate
    '''
    def __init__(self, x, y, width):
        if width < 0:
            raise NonPositiveDigitException('Unable to create triangle: width or height is less than 0')
        else:
            self.x = x
            self.y = y
            self.width = width

    def __str__(self):
        return f'[Triangle: x={self.x}, y={self.y}, width={self.width}]'

    def getArea(self):
        return self.width * self.y / 2

class NonPositiveDigitException(ValueError):
    def __init__(self, message):
        super().__init__(message)
        self.message = message
