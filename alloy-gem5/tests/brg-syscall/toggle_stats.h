#ifndef TOGGLE_STATS_H
#define TOGGLE_STATS_H

inline void toggle_stats(bool on)
{
  __asm__ volatile ("csrw 0x7C1, %0;"
                    :
                    : "r" (on)
                    :);
}

#endif
