# Task 1: Multi-threaded Merge Sort  
Implementation divides the array recursively into sub-arrays, sorting each in separate threads before merging results. We compare the performance between single-threaded and multi-threaded approaches with configurable thread limits.

```bash
python merge_sort.py
python merge_sort.py 50000
```

# Task 2: Multi-threaded Quicksort  
Uses threads to sort partitions concurrently after pivot selection. The controls resource usage with both maximum thread count and recursion depth limits.

```bash
python quicksort.py 
python quicksort.py --size 200000 --threads 8 --depth 4
```

# Task 3: Concurrent File Downloader  
Downloads multiple files in parallel using separate threads. Accepts URLs via command line or text file, with performance comparison between sequential and concurrent downloads.

```bash
python file_downloader.py --urls https://example.com https://python.org
python file_downloader.py --file urls.txt --workers 8
python file_downloader.py --urls https://example.com https://python.org --compare
```
