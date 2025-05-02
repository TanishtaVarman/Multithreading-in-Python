import threading
import time
import random
import sys

sys.setrecursionlimit(10000)

def split(arr, low, high):
    pivot = arr[high]
    i = low - 1
    
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1

def normal_qsort(arr, low=0, high=None):
    if high is None:
        high = len(arr) - 1
    
    if low < high:
        pivot = split(arr, low, high)
        normal_qsort(arr, low, pivot - 1)
        normal_qsort(arr, pivot + 1, high)
    
    return arr

class quick_thread(threading.Thread):
    def __init__(self, arr, low, high):
        threading.Thread.__init__(self)
        self.arr = arr
        self.low = low
        self.high = high
    
    def run(self):
        if self.low < self.high:
            pivot = split(self.arr, self.low, self.high)
            left = quick_thread(self.arr, self.low, pivot - 1)
            right = quick_thread(self.arr, pivot + 1, self.high)
            left.start()
            right.start()
            left.join()
            right.join()

def fast_qsort(arr, low=0, high=None, max_threads=None, depth=0, max_depth=3):
    if high is None:
        high = len(arr) - 1
    
    if low < high:
        pivot = split(arr, low, high)
        
        make_threads = (
            (max_threads is None or threading.active_count() < max_threads) and
            depth < max_depth
        )
        
        if make_threads:
            left = quick_thread(arr, low, pivot - 1)
            right = quick_thread(arr, pivot + 1, high)
            left.start()
            right.start()
            left.join()
            right.join()
        else:
            normal_qsort(arr, low, pivot - 1)
            normal_qsort(arr, pivot + 1, high)
    
    return arr

def time_sort(sort_func, arr, **kwargs):
    arr_copy = arr.copy()
    start = time.time()
    result = sort_func(arr_copy, **kwargs)
    end = time.time()
    return result, end - start

if __name__ == "__main__":
    size = 10000
    numbers = [random.randint(1, 10000) for _ in range(size)]
    
    print(f"sorting {size} numbers")
    
    normal_result, normal_time = time_sort(normal_qsort, numbers)
    print(f"normal sort took: {normal_time:.6f} sec")
    
    configs = [
        {"max_threads": 4, "max_depth": 2},
        {"max_threads": 8, "max_depth": 3},
        {"max_threads": 16, "max_depth": 4}
    ]
    
    for cfg in configs:
        threads = cfg["max_threads"]
        depth = cfg["max_depth"]
        
        thread_result, thread_time = time_sort(fast_qsort, numbers, 
                                             max_threads=threads, max_depth=depth)
        
        assert sorted(thread_result) == normal_result, "wrong result!"
        
        print(f"threaded sort ({threads} threads, {depth} depth): {thread_time:.6f} sec")
        print(f"speed boost: {normal_time / thread_time:.2f}x")
    
    for bigger in [100000, 200000]:
        print(f"\ntesting with {bigger} numbers")
        big_nums = [random.randint(1, 10000) for _ in range(bigger)]
        
        normal_result, normal_time = time_sort(normal_qsort, big_nums)
        print(f"normal sort took: {normal_time:.6f} sec")
        
        thread_result, thread_time = time_sort(fast_qsort, big_nums, 
                                             max_threads=8, max_depth=3)
        print(f"threaded sort (8 threads, 3 depth): {thread_time:.6f} sec")
        print(f"speed boost: {normal_time / thread_time:.2f}x")