#ifndef ULI_H
#define ULI_H

#include <stdint.h>

constexpr uint64_t ULI_SEND_REQ       = 0x832; // CSR_VALUE18
constexpr uint64_t ULI_SEND_RESP      = 0x833; // CSR_VALUE19
constexpr uint64_t ULI_RECV_RESP      = 0x834; // CSR_VALUE20
constexpr uint64_t ULI_RECV_VAL       = 0x835; // CSR_VALUE21
constexpr uint64_t ULI_RECV_SENDER_ID = 0x836; // CSR_VALUE22

// Based on
// The RISC-V Instruction Set Manual
// Volume II: Privileged Architecture
// Document Version 20190608-Priv-MSU-Ratified

constexpr uint64_t CSR_MHARTID  = 0xF14;
constexpr uint64_t CSR_MSTATUS  = 0x300;
constexpr uint64_t CSR_MIDELEG  = 0x303;
constexpr uint64_t CSR_SIDELEG  = 0x103;
constexpr uint64_t CSR_USTATUS  = 0x000;
constexpr uint64_t CSR_UIE      = 0x004;
constexpr uint64_t CSR_UTVEC    = 0x005;
constexpr uint64_t CSR_USCRATCH = 0x040;
constexpr uint64_t CSR_UEPC     = 0x041;
constexpr uint64_t CSR_UCAUSE   = 0x042;
constexpr uint64_t CSR_UTVAL    = 0x043;
constexpr uint64_t CSR_UIP      = 0x044;

constexpr uint64_t CSR_MIDELEG_BIT_USI = 0;
constexpr uint64_t CSR_SIDELEG_BIT_USI = 0;
constexpr uint64_t CSR_MSTATUS_BIT_UIE = 0;

// Get core ID

inline uint64_t core_id()
{
  volatile uint64_t id;
  __asm__ volatile ("csrr %0, %1;" : "=r"(id) : "i"(CSR_MHARTID):);
  return id;
}

// Initialize ULI for the current hart

inline void uli_init()
{
    // Enable global UIE bit in the mstatus
    uint64_t status, deleg;
    __asm__ volatile ("csrr %0, %1;" : "=r"(status) : "i"(CSR_MSTATUS) :);
    status |= (1 << CSR_MSTATUS_BIT_UIE);
    __asm__ volatile ("csrw %0, %1;" :: "i"(CSR_MSTATUS), "r"(status) :);
    // Set USI bit in sideleg and mideleg
    // to delegate ULI handling to the user mode.
    __asm__ volatile ("csrr %0, %1;" : "=r"(deleg) : "i"(CSR_SIDELEG) :);
    deleg |= (1 << CSR_MIDELEG_BIT_USI);
    __asm__ volatile ("csrw %0, %1;" :: "i"(CSR_SIDELEG), "r"(deleg) :);
    __asm__ volatile ("csrr %0, %1;" : "=r"(deleg) : "i"(CSR_MIDELEG) :);
    deleg |= (1 << CSR_SIDELEG_BIT_USI);
    __asm__ volatile ("csrw %0, %1;" :: "i"(CSR_MIDELEG), "r"(deleg) :);
}


// Set ULI handler

inline void uil_set_handler(void* addr)
{
  __asm__ volatile ("csrw %0, %1;"
                    :
                    : "i"(CSR_UTVEC), "r" ((uint64_t)addr << 2)
                    :);
}

// Enable/disable ULI

inline void uli_enable()
{
  __asm__ volatile ("csrw %0, %1;"
                    :
                    : "i"(CSR_UIE), "i" (1)
                    :);
}

inline void uli_disable()
{
  __asm__ volatile ("csrw %0, %1;"
                    :
                    : "i"(CSR_UIE), "i" (0)
                    :);
}

// ULI sender: send a ULI to target core,
// blocked until a resp (or NACK) is received

inline uint64_t uli_send_req(uint64_t target)
{
  // reset ULI_RECV_RESP to zero
  __asm__ volatile ("csrw %0, %1;" :: "i"(ULI_RECV_RESP),  "i" (0) :);
  // send
  __asm__ volatile ("csrw %0, %1;" :: "i"(ULI_SEND_REQ),  "r" (target) :);
  volatile uint64_t resp = 0, val = 0;
  // blocked, waiting for resp
  while (resp == 0) {
    __asm__ volatile ("csrr %0, %1;" : "=r"(resp) : "i"(ULI_RECV_RESP) :);
  }
  __asm__ volatile ("csrr %0, %1;" : "=r"(val) : "i"(ULI_RECV_VAL) :);
  return val;
}

// ULI receiver: send a ULI response to the interrupter

inline void uli_send_resp(uint64_t val = 0)
{
  // send
  __asm__ volatile ("csrw %0, %1;" :: "i"(ULI_SEND_RESP),  "r" (val) :);
}

#endif
