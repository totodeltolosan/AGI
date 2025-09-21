def reverse(text):
    """TODO: Add docstring."""
    return text[::-1]


    """TODO: Add docstring."""
def is_palindrome(text):
    return text == reverse(text)


something = input("Enter text: ")
if is_palindrome(something):
    print("Yes, it is a palindrome")
else:
    print("No, it is not a palindrome")