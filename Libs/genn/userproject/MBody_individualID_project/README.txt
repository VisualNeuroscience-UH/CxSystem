
  Locust olfactory system (Nowotny et al. 2005)
  =============================================

This example is very similar to the MBody1_project example. The only difference is that PN to KC connections are defined with the INDIVIDUALID mechanism.

Like the MBody1_project example this project contains a helper executable called "generate_run", which also
prepares additional synapse connectivity and input pattern data, before compiling and
executing the model. To compile it, simply type:
  nmake /f WINmakefile
for Windows users, or:
  make
for Linux, Mac and other UNIX users. 


  USAGE
  -----

  ./generate_run <0(CPU)/1(GPU)> <nAL> <nKC> <nLH> <nDN> <gscale> <DIR> <MODEL> 
and optional arguments:
DEBUG=0 or DEBUG=1 (default 0): Whether to run in a debugger
FTYPE=DOUBLE of FTYPE=FLOAT (default FLOAT): What floating point type to use
REUSE=0 or REUSE=1 (default 0): Whether to reuse generated connectivity from an earlier run
CPU_ONLY=0 or CPU_ONLY=1 (default 0): Whether to compile in (CUDA independent) "CPU only" mode.

An example invocation of generate_run is:

  ./generate_run 1 100 1000 20 100 0.0025 outname MBody_individualID

Such a command would generate a locust olfaction model with 100 antennal lobe neurons,
1000 mushroom body Kenyon cells, 20 lateral horn interneurons and 100 mushroom body
output neurons, and launch a simulation of it on a CUDA-enabled GPU using single precision floating point numbers. 
All output files will be prefixed with "outname" and will be created under the "outname" directory.

In more details, what generate_run program does is: 
a) use some other tools to generate the appropriate connectivity
   matrices and store them in files.

b) build the source code for the model by writing neuron numbers into
   userproject/include/sizes.h, and executing "buildmodel.sh MBody1 [DEBUG OFF/ON]".  

c) compile the generated code by invoking "make clean && make" 
   running the code, e.g. "./classol_sim r1 1".

  ./generate_run 0 100 1000 20 100 0.0025 outname MBody_individualID FTYPE=DOUBLE CPU_ONLY=1


  MODEL INFORMATION
  -----------------

For information regarding the locust olfaction model implemented in this example project, see:

T. Nowotny, R. Huerta, H. D. I. Abarbanel, and M. I. Rabinovich Self-organization in the
olfactory system: One shot odor recognition in insects, Biol Cyber, 93 (6): 436-446 (2005),
doi:10.1007/s00422-005-0019-7 
