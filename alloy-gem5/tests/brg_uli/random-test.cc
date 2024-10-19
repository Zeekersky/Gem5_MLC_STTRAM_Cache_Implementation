#include <pthread.h>
#include <unistd.h>

#include <atomic>
#include <cstdarg>
#include <cstdio>
#include <cstdlib>
#include <iostream>
#include <mutex>

#include "uli.h"

constexpr int NTHREADS = 16;
std::atomic<int> g_barrier(NTHREADS);

extern "C" {

void handler_trampoline(); // call into assembly trampoline

void handler_func()
{
  printf("Core %ld: I received an ULI!\n", core_id());
  // send response
  uli_send_resp(2);
}

}

// wait x iterations

void wait(uint64_t r)
{
  volatile uint64_t i = 0;
  while (i < r) {
    i++;
  }
}

void* thread_func(void* arg)
{
  uli_init();
  uil_set_handler((void*)&handler_trampoline);
  uli_enable();

  long id = (long) arg;
  g_barrier--;
  while (g_barrier > 0);

  while (true) {
    // wait
    int wait_time = rand() % 10000;
    wait(wait_time);
    // flip a coin
    int coin = rand() % 2;
    if (coin == 0) {
      uli_disable();
      long target = id;
      while (target == id)
        target = rand() % NTHREADS;
      int val = uli_send_req(target);
      printf("Core %ld: I recieved an %s from Core %ld\n", core_id(),
             val ? "Ack" : "Nack", target);
      uli_enable();
    } else {
      wait_time = rand() % 10000;
      wait(wait_time);
    }
  }
}

int main(int argc, char* argv[])
{

  pthread_t threads[NTHREADS];

  printf("Random test starts, handler_trampoline's"
         "address = %p\n", &handler_trampoline);

  for (int i = 1; i < NTHREADS; i++) {
    pthread_create(&threads[i], NULL, thread_func, (void*) i);
  }

  uli_init();
  uil_set_handler((void*)&handler_trampoline);
  uli_enable();

  thread_func(NULL);

  return 0;
}
