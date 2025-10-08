import multiprocessing

def worker_function(name, value):
    """A function to be executed in a separate process."""
    print(f"Process {name} received value: {value}")
    # Simulate some work
    import time
    time.sleep(value)
    print(f"Process {name} finished.")

if __name__ == '__main__':
    # Create Process instances, passing arguments as a tuple to 'args'
    processes = []
    for i in range(10):
        p = multiprocessing.Process(target=worker_function, args=(f'{i}', i))
        processes.append(p)

    # Start the processes
    for p in processes:
        p.start()

    for p in processes:
        p.join()
    # process1.start()
    # process2.start()
    # process3.start()

    # # Wait for all processes to complete
    # process1.join()
    # process2.join()
    # process3.join()

    print("Main process: All worker processes have completed their tasks.")