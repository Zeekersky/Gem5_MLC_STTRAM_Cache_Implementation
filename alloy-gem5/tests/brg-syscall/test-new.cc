//========================================================================
// test-new.cc
//========================================================================
// Test invoking new on multiple threads

#include <unistd.h>

#include <atomic>
#include <cstdarg>
#include <cstdio>
#include <cstdlib>
#include <iostream>
#include <mutex>
#include <thread>
#include <vector>

#include "toggle_stats.h"

void func(const int num_news, const int size)
{
  int* t;
  for (int i = 0; i < num_news; i++) {
    t = new int[size];
    delete [] t;
  }
}

int main(int argc, char* argv[])
{
  int in_timing_loop = 0;     // whether do syscall in the timing loop
  int nthreads       = 1;     // number of threads
  int num_news       = 100;   // number of news invoked
  int size           = 1024;  // size of each new

  if (argc > 1) {
    in_timing_loop = atoi(argv[1]);
  }

  if (argc > 2) {
    nthreads = atoi(argv[2]);
  }

  if (argc > 3) {
    num_news = atoi(argv[3]);
  }

  if (argc > 4) {
    size = atoi(argv[4]);
  }

  std::vector< std::thread > threads;

  if (in_timing_loop > 0) {
    toggle_stats(true);
  }

  for (int n = 1; n < nthreads; n++) {
    threads.emplace_back( [&] {
      func(num_news, size);
    } );
  }

  func(num_news, size);

  if (in_timing_loop > 0) {
    toggle_stats(false);
  }

  for (auto& t : threads) {
    t.join();
  }

  return 0;
}
