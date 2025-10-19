from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
import time

# https://superfastpython.com/threadpool-python/
def task(name, duration):
    time.sleep(duration)
    return f"Task {name} completed after {duration} seconds."

if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=1) as executor:
        start = time.time()
        futures = [
            executor.submit(task, "A", 2),
            executor.submit(task, "B", 1),
            executor.submit(task, "C", 3)
        ]

        # Wait for all futures to complete
        done, not_done = wait(futures, return_when=ALL_COMPLETED)

        print("All tasks are done:")
        for future in done:
            print(future.result())

        end = time.time()

        print(f'took {(end - start)}')