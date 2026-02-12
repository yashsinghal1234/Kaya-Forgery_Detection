def fib(n):
    # quick fib calc
    if n<2:
        return n
    a,b=0,1
    for _ in range(n-1):
        a,b=b,a+b
    return b

def fact(num):
    res=1
    for i in range(2,num+1):
        res*=i
    return res

# some helper funcs
def is_prime(x):
    if x<2: return False
    for i in range(2,int(x**0.5)+1):
        if x%i==0:
            return False
    return True

def get_primes(limit):
    primes=[]
    for n in range(2,limit):
        if is_prime(n):
            primes.append(n)
    return primes
"""
This module provides functionality for calculating Fibonacci sequences.

This function is used to calculate the Fibonacci sequence up to n terms.
"""

def calculate_fibonacci(n):
    """
    Calculate the Fibonacci sequence.
    
    This function will generate a Fibonacci sequence with n elements.
    
    Args:
        n: The number of Fibonacci numbers to generate
    
    Returns:
        A list containing the Fibonacci sequence
    
    Example:
        >>> calculate_fibonacci(5)
        [0, 1, 1, 2, 3]
    """
    # Initialize the result list
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]
    
    # Create a list to store the Fibonacci sequence
    fibonacci_sequence = [0, 1]
    
    # Iterate through the remaining numbers
    for i in range(2, n):
        # Calculate the next Fibonacci number
        next_number = fibonacci_sequence[i-1] + fibonacci_sequence[i-2]
        # Append to the sequence
        fibonacci_sequence.append(next_number)
    
    # Return the result
    return fibonacci_sequence


def factorial(n):
    """
    This function calculates the factorial of a number.
    
    Args:
        n: The number to calculate factorial for
    
    Returns:
        The factorial result
    """
    # Initialize the result variable
    result = 1
    
    # Iterate through all numbers from 1 to n
    for i in range(1, n + 1):
        # Multiply the result by the current number
        result = result * i
    
    # Return the final result
    return result

