import threading
import time
import requests
import os
import argparse
from urllib.parse import urlparse

class Downloader(threading.Thread):
    def __init__(self, url, save_folder='.'):
        threading.Thread.__init__(self)
        self.url = url
        self.save_folder = save_folder
        self.done = False
        self.time_taken = 0
        
    def run(self):
        try:
            start = time.time()
            
            parsed = urlparse(self.url)
            filename = os.path.basename(parsed.path)
            
            if not filename:
                filename = f"{parsed.netloc}-{hash(self.url) % 10000}.html"
            
            save_path = os.path.join(self.save_folder, filename)
            
            # Download file
            response = requests.get(self.url, stream=True)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            self.time_taken = time.time() - start
            self.done = True
            print(f"downloaded {self.url} to {save_path} in {self.time_taken:.2f} sec")
            
        except Exception as e:
            self.time_taken = time.time() - start
            print(f"failed to download {self.url}: {str(e)}")

def download_one_by_one(urls, save_folder='.'):
    start = time.time()
    results = []
    
    for url in urls:
        try:
            parsed = urlparse(url)
            filename = os.path.basename(parsed.path)
            
            if not filename:
                filename = f"{parsed.netloc}-{hash(url) % 10000}.html"
            
            save_path = os.path.join(save_folder, filename)
            
            url_start = time.time()
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            time_spent = time.time() - url_start
            results.append((url, True, time_spent))
            print(f"downloaded {url} to {save_path} in {time_spent:.2f} sec")
            
        except Exception as e:
            time_spent = time.time() - url_start
            results.append((url, False, time_spent))
            print(f"failed to download {url}: {str(e)}")
    
    total_time = time.time() - start
    return results, total_time

def download_many_at_once(urls, save_folder='.', max_workers=5):

    start = time.time()
    os.makedirs(save_folder, exist_ok=True)
    workers = []
    
    for url in urls:
        worker = Downloader(url, save_folder)
        workers.append(worker)
        worker.start()
        
        if max_workers and len(workers) >= max_workers:
            for w in workers:
                if w.is_alive():
                    w.join(0.1)
                    if not w.is_alive():
                        workers.remove(w)
                        break
    
    for worker in workers:
        worker.join()
    
    results = [(w.url, w.done, w.time_taken) for w in workers]
    total_time = time.time() - start
    
    return results, total_time

def get_urls_from_file(file_path):
    """Read URLs from a text file"""
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def main():
    parser = argparse.ArgumentParser(description='download files fast or slow')
    parser.add_argument('--urls', nargs='+', help='list of urls to download')
    parser.add_argument('--file', help='file with urls, one per line')
    parser.add_argument('--folder', default='downloads', help='where to save files')
    parser.add_argument('--workers', type=int, default=5, help='max download threads')
    parser.add_argument('--slow', action='store_true', help='download one at a time')
    parser.add_argument('--compare', action='store_true', help='try both methods')
    
    args = parser.parse_args()
    
  
    urls = []
    if args.urls:
        urls = args.urls
    elif args.file:
        urls = get_urls_from_file(args.file)
    else:
        urls = [
            'https://www.example.com',
            'https://www.python.org',
            'https://www.github.com',
            'https://www.wikipedia.org',
            'https://www.stackoverflow.com'
        ]
        print("no urls given, using some examples")
    
    os.makedirs(args.folder, exist_ok=True)
    

    if args.slow or args.compare:
        print(f"\ndownloading {len(urls)} files one by one...")
        slow_results, slow_time = download_one_by_one(urls, args.folder)
        print(f"\nfinished in {slow_time:.2f} sec")
        good = sum(1 for _, ok, _ in slow_results if ok)
        print(f"successful: {good}/{len(urls)}")
    
    if not args.slow or args.compare:
        print(f"\ndownloading {len(urls)} files with {args.workers} workers...")
        fast_results, fast_time = download_many_at_once(urls, args.folder, args.workers)
        print(f"\nfinished in {fast_time:.2f} sec")
        good = sum(1 for _, ok, _ in fast_results if ok)
        print(f"successful: {good}/{len(urls)}")
    
    # Show comparison if requested
    if args.compare:
        speed_boost = slow_time / fast_time if fast_time > 0 else 0
        print(f"\ncomparison:")
        print(f"one-by-one time: {slow_time:.2f} sec")
        print(f"multi-worker time: {fast_time:.2f} sec")
        print(f"speed boost: {speed_boost:.2f}x")

