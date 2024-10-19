echo "building sc3..."
scons -j144 build/RISCV_SC3_Two_Level/gem5.opt --default=RISCV PROTOCOL=SC3_Two_Level
echo "building denovo..."
scons -j144 build/RISCV_DeNovo_Two_Level/gem5.opt --default=RISCV PROTOCOL=DeNovo_Two_Level
echo "building mesi..."
scons -j144 build/RISCV_MESI_Two_Level/gem5.opt --default=RISCV PROTOCOL=MESI_Two_Level
