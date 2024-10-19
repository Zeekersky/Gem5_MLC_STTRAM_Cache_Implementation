#include <pthread.h>
#include <unistd.h>

#include <atomic>
#include <cstdarg>
#include <cstdio>
#include <cstdlib>
#include <iostream>
#include <mutex>

#include "uli.h"

volatile int x = 1;

extern "C" {

void handler_trampoline(); // call into assembly trampoline

void handler_func()
{
  printf("Core %ld: I received an ULI!\n", core_id());
  x--;
  uli_send_resp(2);
}

}

std::atomic<int> b(1); // a global barrier

void* thread_func(void*)
{
  uli_init();
  uil_set_handler((void*)&handler_trampoline);
  uli_enable();

  b--; // notify core 0 to interrupt me

  while (x); // wait until the handler to unset x

  uli_disable();

  return NULL;
}

int main(int argc, char* argv[])
{
  printf("handler_func addr = %p\n", &handler_func);
  pthread_t thread;
  pthread_create(&thread, NULL, thread_func, NULL);

  while (b); // wait thread 1 to finish setup

  uint64_t resp = uli_send_req(1);
  printf("Core %ld: ULI resp value = %ld\n", core_id(), resp);

  pthread_join(thread, NULL);

  return 0;
}
