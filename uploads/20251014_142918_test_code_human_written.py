def fib(n):
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

# quick utility to check palindrome
def is_palindrome(s):
    return s==s[::-1]

class DataProcessor:
    def __init__(self,data):
        self.data=data
        self.processed=False

    def filter_evens(self):
        return [x for x in self.data if x%2==0]

    def get_stats(self):
        if not self.data: return None
        return {
            'min':min(self.data),
            'max':max(self.data),
            'avg':sum(self.data)/len(self.data)
        }
