#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
This module implements a threadpool which allows scripts that require 
performing concurrent jobs, an efficient and thread safe way to do this.
 
The two classes available are ThreadPool and Thread. ThreadPool is the 
controller class and contains a collection of Thread objects, which must be
subclassed.
Any thread can add a job to the ThreadPool by calling its append() method.
The pool will add this task to the jobqueue and activate a sleeping thread, if
available. In case no thread is directly available, the job will be handled by
the first free thread.
 
The Thread class must be subclassed and passed to the ThreadPool's constructor.
The subclass should implement a do(args) method, which will receive as its 
argument the job. Please note that providing mutable variables to the jobqueue
may cause thread unsafety!
"""
#
# (C) Bryan Tong Minh, 2007
#
# Distributed under the terms of the MIT license.
#
__version__ = '$Id$'
#
 
import sys, threading
 
class ThreadPool(dict):
    pools = []
    def __init__(self, worker):
        dict.__init__(self)
 
        self.jobLock = threading.Lock()
        self.jobQueue = []
        self.worker = worker
        self.threads = []
 
        self.pools.append(self)
 
    def append(self, job):
        self.jobLock.acquire()
        try:
            self.jobQueue.append(job)
            unlock_workers = len(self.jobQueue)
     
            counter = 0
            for event in self.itervalues():
                if not event.isSet():
                    event.set()
                    counter += 1
                if counter == unlock_workers:
                    break
        finally:
            self.jobLock.release()
 
    def add_thread(self, *args, **kwargs):
        self.jobLock.acquire()
        try:
            thread = self.worker(self, *args, **kwargs)
            self.threads.append(thread)
            self[id(thread)] = threading.Event()
        finally:
            self.jobLock.release()
 
    def start(self):
        for thread in self.threads:
            if not thread.isAlive():
                thread.start()
    def exit(self):
        self.jobLock.acquire()
        try:
            del self.jobQueue[:]
            for thread in self.threads:
                thread.quit = True
                self[id(thread)].set()
        finally:
            self.jobLock.release()
 
class Thread(threading.Thread):
    def __init__(self, pool):
        threading.Thread.__init__(self)
        self.pool = pool
        self.quit = False
 
    def run(self):
	while True:
		# No try..finally: lock.release() here:
		# The lock might be released twice, in case
		# the thread waits for an event, a race 
		# condition might occur where a lock is released
		# that is acquired by another thread. 
		self.pool.jobLock.acquire()

		if self.quit:
			return
	
		if not self.pool.jobQueue:
			# In case no job is available, wait for the pool 
			# to  call and do not start a busy while loop.
			event = self.pool[id(self)]
			self.pool.jobLock.release()
			event.clear()
			event.wait()
			continue
		job = self.pool.jobQueue.pop(0)
		self.pool.jobLock.release()
	
		self.do(job)
 
    def exit(self):
        self.pool.jobLock.acquire()
        try:
            self.quit = True
            self.pool[id(self)].set()
        finally:
            self.pool.jobLock.release()
 
def catch_signals():
    import signal
    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)
 
def sig_handler(signal, stack):
    for pool in ThreadPool.pools:
        pool.exit()
    sys.exit()
 
if __name__ == '__main__':
    import time
    # Test cases
 
    class Worker(Thread):
        def do(self, args):
            print 'Working', self
            time.sleep(10)
            print 'Done', self
 
    pool = ThreadPool(Worker)
    print 'Spawning 5 threads'
    [pool.add_thread() for i in xrange(5)]
    pool.start()
 
    print 'Doing 25 jobs'
    for i in xrange(25):
        print 'Job', i
        pool.append(i)
        time.sleep(i % 6)
 
    for thread in pool.threads:
        thread.exit()

