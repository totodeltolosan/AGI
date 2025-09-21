class Person:
    """TODO: Add docstring."""
        """TODO: Add docstring."""
    def __init__(self, name):
        self.name = name
            """TODO: Add docstring."""

    def say_hi(self):
        print('Hello, my name is', self.name)

p = Person('Swaroop')
p.say_hi()
# The previous 2 lines can also be written as
# Person('Swaroop').say_hi()