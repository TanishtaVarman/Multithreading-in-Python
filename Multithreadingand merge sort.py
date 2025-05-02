import threading
import time
import random

def merg(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

def normal_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = normal_sort(arr[:mid])
    right = normal_sort(arr[mid:])
    return merg(left, right)

class thread_sort(threading.Thread):
    def __init__(self, arr):
        threading.Thread.__init__(self)
        self.arr = arr
        self.sorted = None
    
    def run(self):
        if len(self.arr) <= 1:
            self.sorted = self.arr
            return
        mid = len(self.arr) // 2
        left = thread_sort(self.arr[:mid])
        right = thread_sort(self.arr[mid:])
        left.start()
        right.start()
        left.join()
        right.join()
        self.sorted = merg(left.sorted, right.sorted)

def fast_sort(arr, max_threads=None):
    if max_threads is None or threading.active_count() < max_threads:
        if len(arr) <= 1:
            return arr
        mid = len(arr) // 2
        left = thread_sort(arr[:mid])
        right = thread_sort(arr[mid:])
        left.start()
        right.start()
        left.join()
        right.join()
        return merg(left.sorted, right.sorted)
    else:
        return normal_sort(arr)

def time_it(sort_func, arr, **kwargs):
    start = time.time()
    result = sort_func(arr.copy(), **kwargs)
    end = time.time()
    return result, end - start

if __name__ == "__main__":
    size = 10000
    numbers = [random.randint(1, 10000) for _ in range(size)]
    print(f"sorting {size} numbers")
    
    normal_result, normal_time = time_it(normal_sort, numbers)
    print(f"normal sort took: {normal_time:.6f} sec")
    
    thread_options = [None, 4, 8, 16]
    for threads in thread_options:
        label = "no limit" if threads is None else threads
        thread_result, thread_time = time_it(fast_sort, numbers, max_threads=threads)
        assert thread_result == normal_result, "wrong result!"
        print(f"threaded sort ({label} threads) took: {thread_time:.6f} sec")
        print(f"speed boost: {normal_time / thread_time:.2f}x")
    
    for bigger in [100000, 200000]:
        print(f"\ntesting with {bigger} numbers")
        big_numbers = [random.randint(1, 10000) for _ in range(bigger)]
        normal_result, normal_time = time_it(normal_sort, big_numbers)
        print(f"normal sort took: {normal_time:.6f} sec")
        thread_result, thread_time = time_it(fast_sort, big_numbers, max_threads=8)
        print(f"threaded sort (8 threads) took: {thread_time:.6f} sec")
        print(f"speed boost: {normal_time / thread_time:.2f}x")