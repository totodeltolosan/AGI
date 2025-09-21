x = 50


def func():
    """TODO: Add docstring."""
    global x

    print('x is', x)
    x = 2
    print('Changed global x to', x)


func()
print('Value of x is', x)