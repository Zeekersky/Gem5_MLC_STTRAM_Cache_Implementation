#=========================================================================
# Simple C/C++ Makefile
#=========================================================================
# Author: Moyang Wang

#-------------------------------------------------------------------------
# Path config
#-------------------------------------------------------------------------

#-------------------------------------------------------------------------
# Source
#-------------------------------------------------------------------------

C_SRCS   = $(wildcard *.c)
CPP_SRCS = $(wildcard *.cc)
OBJS = $(subst .c,.o,$(C_SRCS)) $(subst .cc,.o,$(CPP_SRCS))
EXEC = $(subst .o,,$(OBJS))

#-------------------------------------------------------------------------
# C/C++ Compiler
#-------------------------------------------------------------------------
# riscv64-unknown-linux-gnu-g++ -std=c++11 -static -Wl,--whole-archive -lpthread -latomic -Wl,--no-whole-archive

CC  = riscv64-unknown-linux-gnu-gcc
CXX = riscv64-unknown-linux-gnu-g++

#-------------------------------------------------------------------------
# Compiler flags
#-------------------------------------------------------------------------

CPPFLAGS = -std=c++11 -static
LDFLAGS  = -Wl,--whole-archive -lpthread -latomic -Wl,--no-whole-archive
LDLIBS   =
DAFLAGS  = -dC

#-------------------------------------------------------------------------
# Include/link paths
#-------------------------------------------------------------------------

INC_PATHS = .
LD_PATHS  = .

CPPFLAGS += $(foreach d, $(INC_PATHS), -I$d)
LDFLAGS  += $(foreach d, $(LD_PATHS), -L$d)

#-------------------------------------------------------------------------
# Build targets
#-------------------------------------------------------------------------

.SECONDEXPANSION:
.PHONY: all clean

all: $(EXEC)

$(EXEC): $$(@).cc
	$(CXX) $(CPPFLAGS) $(LDFLAGS) -o $@  $^ $(LDLIBS)

clean:
	rm -rf $(EXEC)

default: all
