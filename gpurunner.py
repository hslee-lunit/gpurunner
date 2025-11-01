"""This module is used to keep GPUs busy. This is needed to avoid the job being killed by the scheduler."""
import argparse
import multiprocessing
import random
import time
from time import sleep
from typing import List

import torch

_SLEEP_TIME = 0
_MATRIX_SIZE = 30000


def _dummy_gpu_task(
    gpu_id: int,
    stop_event: multiprocessing.Event,
    sleep_time: float = _SLEEP_TIME,
    matrix_size: int = _MATRIX_SIZE,
    enable_jitter: bool = False,
    jitter_min_interval: float = 1.0,
    jitter_max_interval: float = 20.0,
    jitter_min_duration: float = 1.0,
    jitter_max_duration: float = 10.0,
    jitter_sleep_multiplier: float = 5.0,
):
    """This is a dummy function to keep the GPU with id `gpu_id` busy.

    By tuning the sleeping time, you can adjust the GPU utilization.
    
    Args:
        gpu_id: The GPU device ID to use
        stop_event: Event to signal the process to stop
        sleep_time: Base sleep time between operations
        matrix_size: Size of the matrix for computation
        enable_jitter: Whether to enable utilization jittering
        jitter_min_interval: Minimum time (seconds) before next jitter occurs
        jitter_max_interval: Maximum time (seconds) before next jitter occurs
        jitter_min_duration: Minimum duration (seconds) of a jitter event
        jitter_max_duration: Maximum duration (seconds) of a jitter event
        jitter_sleep_multiplier: Multiplier for sleep_time during jitter (higher = lower GPU util)
    """
    torch.cuda.set_device(gpu_id)

    data = torch.randn(matrix_size, matrix_size).cuda()
    
    # Initialize jitter tracking
    next_jitter_time = None
    jitter_end_time = None

    print(f"GPU {gpu_id}: Running")
    
    if enable_jitter:
        next_jitter_time = time.time() + random.uniform(jitter_min_interval, jitter_max_interval)
        print(f"GPU {gpu_id}: Next {next_jitter_time - time.time():.1f}s")
    
    while not stop_event.is_set():
        torch.matmul(data, data)

        current_sleep_time = sleep_time
        
        # Handle jittering logic
        if enable_jitter:
            current_time = time.time()
            
            # Check if we should start a jitter event
            if jitter_end_time is None and current_time >= next_jitter_time:
                jitter_duration = random.uniform(jitter_min_duration, jitter_max_duration)
                jitter_end_time = current_time + jitter_duration
                print(f"GPU {gpu_id}: Start {jitter_duration:.1f}s")
            
            # Check if we're in a jitter event
            if jitter_end_time is not None:
                if current_time < jitter_end_time:
                    # We're in a jitter event - reduce utilization
                    current_sleep_time = sleep_time * jitter_sleep_multiplier
                else:
                    # Jitter event ended - schedule next one
                    next_jitter_interval = random.uniform(jitter_min_interval, jitter_max_interval)
                    next_jitter_time = current_time + next_jitter_interval
                    jitter_end_time = None
                    print(f"GPU {gpu_id}: Ends {next_jitter_interval:.1f}s")
        
        sleep(current_sleep_time)


class DummyGPUProcesses:
    """This class is used to keep GPUs busy. This is needed to avoid"""
    def __init__(
        self,
        gpu_ids: List[int],
        sleep_time: float = _SLEEP_TIME,
        matrix_size: int = _MATRIX_SIZE,
        enable_jitter: bool = False,
        jitter_min_interval: float = 30.0,
        jitter_max_interval: float = 120.0,
        jitter_min_duration: float = 5.0,
        jitter_max_duration: float = 20.0,
        jitter_sleep_multiplier: float = 10.0,
    ):
        # multiprocessing is set to `spawn` because CUDA requires it
        multiprocessing.set_start_method('spawn', force=True)

        self._stop_events: List[multiprocessing.Event] = []
        self._gpu_processes: List[multiprocessing.Process] = []

        for gpu_id in gpu_ids:
            _stop_event = multiprocessing.Event()
            self._stop_events.append(_stop_event)
            self._gpu_processes.append(multiprocessing.Process(
                target=_dummy_gpu_task, args=(gpu_id, _stop_event, sleep_time, matrix_size)))

    def start(self):
        """Start dummy GPU workers"""
        for process in self._gpu_processes:
            process.start()

    def stop(self):
        """Stop dummy GPU workers"""
        for event in self._stop_events:
            event.set()
        for process in self._gpu_processes:
            process.join()
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--hours-to-run", type=int, default=None)
    parser.add_argument("--sleep-time", type=float, default=_SLEEP_TIME)
    parser.add_argument("--matrix-size", type=int, default=_MATRIX_SIZE)
    args = parser.parse_args()
    hours_to_run = args.hours_to_run

    # Detect the available GPUs
    gpu_ids = torch.cuda.device_count()

    try:
        dummy_gpu = DummyGPUProcesses(
            gpu_ids=list((range(gpu_ids))), sleep_time=args.sleep_time, matrix_size=args.matrix_size
        )
        # Starts the dummy GPU workers.
        dummy_gpu.start()
        if hours_to_run is not None:
            time_to_run = hours_to_run * 3600
            sleep(time_to_run)
            dummy_gpu.stop()
            print("The dummy GPU workers are stopped successfully.")
        else:
            while True:
                # Run forever.
                sleep(1)
    except KeyboardInterrupt:
        dummy_gpu.stop()
        print("The dummy GPU workers are stopped successfully.")
    except Exception as e:
        dummy_gpu.stop()
        print(f"Error starting dummy GPU workers: {e}")
        raise e

