.text
.align 2
.global handler_trampoline

handler_trampoline:

# Save caller-saved registers:
# We don't know which registers the real handler_func uses
# so we have to save them all...
addi sp, sp, -136
sd ra, 8(sp)
sd t0, 16(sp)
sd t1, 24(sp)
sd t2, 32(sp)
sd t3, 40(sp)
sd t4, 48(sp)
sd t5, 56(sp)
sd t6, 64(sp)
sd a0, 72(sp)
sd a1, 80(sp)
sd a2, 88(sp)
sd a3, 96(sp)
sd a4, 104(sp)
sd a5, 112(sp)
sd a6, 120(sp)
sd a7, 128(sp)

# Call handler_func：
#   extern "C" { void handler_func(); }
call handler_func

# Restore registers
ld ra, 8(sp)
ld t0, 16(sp)
ld t1, 24(sp)
ld t2, 32(sp)
ld t3, 40(sp)
ld t4, 48(sp)
ld t5, 56(sp)
ld t6, 64(sp)
ld a0, 72(sp)
ld a1, 80(sp)
ld a2, 88(sp)
ld a3, 96(sp)
ld a4, 104(sp)
ld a5, 112(sp)
ld a6, 120(sp)
ld a7, 128(sp)
addi sp, sp, 136

# uret: return from user-level interrupt
#   uie     <- upie
#   next pc <- uepc
uret
