# Add 12 and 30 and store the result at address 258.
ACC = 12;
MEM[256] = ACC;
ACC = 30;
MEM[257] = ACC;
ACC = 256;
ACC = MEM[ACC];
ACC = ACC + MEM[257];
MEM[258] = ACC;
