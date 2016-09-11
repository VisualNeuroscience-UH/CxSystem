/*--------------------------------------------------------------------------
   Author: Thomas Nowotny
  
   Institute: Center for Computational Neuroscience and Robotics
              University of Sussex
	      Falmer, Brighton BN1 9QJ, UK 
  
   email to:  T.Nowotny@sussex.ac.uk
  
   initial version: 2010-02-07
  
--------------------------------------------------------------------------*/

//--------------------------------------------------------------------------
/*! \file generate_izhikevich_network_run.cc

\brief This file is part of a tool chain for running the classIzh/Izh_sparse example model.

This file compiles to a tool that wraps all the other tools into one chain of tasks, including running all the gen_* tools for generating connectivity, providing the population size information through ../userproject/include/sizes.h to the model definition, running the GeNN code generation and compilation steps, executing the model and collecting some timing information. This tool is the recommended way to quickstart using GeNN as it only requires a single command line to execute all necessary tasks.
*/ 
//--------------------------------------------------------------------------

#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include <cstdlib>
#include <cmath>
#include <locale>
using namespace std;

#ifdef _WIN32
#include <direct.h>
#include <stdlib.h>
#else // UNIX
#include <sys/stat.h> // needed for mkdir?
#endif

#include "command_line_processing.h"

/////////////////////////
unsigned int openFileGetMax(unsigned int * array, unsigned int size, string name) {
  unsigned int maxConn = 0;
  FILE *f = fopen(name.c_str(), "rb");
  int retval = fread(array, (size + 1) * sizeof(unsigned int), 1, f);
  for (unsigned int i = 0; i < size; i++) {
    unsigned int connNo = array[i + 1] - array[i];
    if (connNo > maxConn) maxConn = connNo;
  }
  fprintf(stderr, " \n maximum postsynaptic connection per neuron in the 1st group is %u , fread returned %d values\n", maxConn, retval);
  return maxConn;
}
/////////////////////////

//--------------------------------------------------------------------------
/*! \brief Main entry point for generate_run.
 */
//--------------------------------------------------------------------------

int main(int argc, char *argv[])
{
  if (argc < 8)
  {
    cerr << "usage: generate_run <CPU=0, AUTO GPU=1, GPU n= \"n+2\"> <nNeurons> <nConn> <gscale> <outdir> <model name> <input fac> <OPTIONS> \n\
Possible options: \n\
DEBUG=0 or DEBUG=1 (default 0): Whether to run in a debugger \n\
FTYPE=DOUBLE of FTYPE=FLOAT (default FLOAT): What floating point type to use \n\
REUSE=0 or REUSE=1 (default 0): Whether to reuse generated connectivity from an earlier run \n\
CPU_ONLY=0 or CPU_ONLY=1 (default 0): Whether to compile in (CUDA independent) \"CPU only\" mode." << endl;
    exit(1);
  }
  int retval;
  string cmd;
  string gennPath= getenv("GENN_PATH");
  int which = atoi(argv[1]);
  int nTotal = atoi(argv[2]);
  int nExc = ceil((float) 4 * nTotal / 5);
  int nInh = nTotal - nExc;
  int nConn = atoi(argv[3]);
  float gscale = atof(argv[4]);
  string outDir = toString(argv[5]) + "_output";  
  string outDir_g = "inputfiles";  
  string modelName = argv[6];
  double inputFac= atof(argv[7]);
  float meangExc = 0.5 * gscale;
  float meangInh = -1.0 * gscale;

  int argStart= 8;
#include "parse_options.h"

  // create output directories
#ifdef _WIN32
  _mkdir(outDir.c_str());
  _mkdir(outDir_g.c_str());
#else // UNIX
  if (mkdir(outDir.c_str(), S_IRWXU | S_IRWXG | S_IXOTH) == -1) {
    cerr << "Directory cannot be created. It may exist already." << endl;
  }
  if (mkdir(outDir_g.c_str(), S_IRWXU | S_IRWXG | S_IXOTH) == -1) {
    cerr << "Directory cannot be created. It may exist already." << endl;
  }
#endif

  if (fixsynapse == 0) {
    // generate network connectivity patterns
    cmd = gennPath + "/userproject/tools/gen_syns_sparse_izhModel ";
    cmd += toString(nTotal) + " ";
    cmd += toString(nConn) + " ";
    cmd += toString(meangExc) + " ";
    cmd += toString(meangInh) + " ";
    cmd += outDir_g + "/g" + modelName;
    retval=system(cmd.c_str());
    if (retval != 0){
      cerr << "ERROR: Following call failed with status " << retval << ":" << endl << cmd << endl;
      cerr << "Exiting..." << endl;
      exit(1);
    }
  }

  // read connectivity patterns to get maximum connection per neuron for each synapse population
  // population neuron numbers are for sources in the order in currentmodel.cc
  unsigned int *indInG = new unsigned int[nTotal]; // allocate the biggest possible, the we will only use what we need
  string name = outDir_g + "/g" + modelName + "_indInG_ee";
  unsigned int maxN0 = openFileGetMax(indInG, nExc, name);
  name = outDir_g + "/g" + modelName + "_indInG_ei";
  unsigned int maxN1 = openFileGetMax(indInG, nExc, name);
  name = outDir_g + "/g" + modelName + "_indInG_ie";
  unsigned int maxN2 = openFileGetMax(indInG, nInh, name);
  name = outDir_g + "/g" + modelName + "_indInG_ii";
  unsigned int maxN3 = openFileGetMax(indInG, nInh, name);
  delete[] indInG;
  ////////////////////////////////

  // write neuron population sizes
  string fname = gennPath + "/userproject/include/sizes.h";
  ofstream os(fname.c_str());
  if (which > 1) {
    os << "#define nGPU " << which-2 << endl;
    which= 1;
  }
  os << "#define _NExc " << nExc << endl;
  os << "#define _NInh " << nInh << endl;
  os << "#define _NMaxConnP0 " << maxN0 << endl;
  os << "#define _NMaxConnP1 " << maxN1 << endl;
  os << "#define _NMaxConnP2 " << maxN2 << endl;
  os << "#define _NMaxConnP3 " << maxN3 << endl;
  os << "#define inputFac " << inputFac << endl;
  string tmps= tS(ftype);
  os << "#define _FTYPE " << "GENN_" << toUpper(tmps) << endl;
  os << "#define scalar " << toLower(tmps) << endl;
  if (toLower(ftype) == "double") {
      os << "#define SCALAR_MIN DBL_MIN" << endl;
      os << "#define SCALAR_MAX DBL_MAX" << endl;
  }
  else {
      os << "#define SCALAR_MIN FLT_MIN" << endl;
      os << "#define SCALAR_MAX FLT_MAX" << endl;
  } 

  os.close();
  
  // build it
#ifdef _WIN32
  cmd = "cd model && buildmodel.bat " + modelName + " DEBUG=" + toString(dbgMode);
  if (cpu_only) {
      cmd += " CPU_ONLY=1";
  }
  cmd += " && nmake /nologo /f WINmakefile clean && nmake /nologo /f WINmakefile";
  if (dbgMode == 1) {
    cmd += " DEBUG=1";
  }
  if (cpu_only) {
      cmd += " CPU_ONLY=1";
  }
  
#else // UNIX
  cmd = "cd model && buildmodel.sh " + modelName + " DEBUG=" + toString(dbgMode);
  if (cpu_only) {
      cmd += " CPU_ONLY=1";
  }
  cmd += " && make clean && make";
  if (cpu_only) {
      cmd += " CPU_ONLY=1";
  }
  else {
      if (dbgMode == 1) {
	  cmd += " debug";
      }
      else {
	  cmd += " release";
      }
  }
#endif
  retval=system(cmd.c_str());
  if (retval != 0){
    cerr << "ERROR: Following call failed with status " << retval << ":" << endl << cmd << endl;
    cerr << "Exiting..." << endl;
    exit(1);
  }

  // run it!
  cout << "running test..." << endl;
#ifdef _WIN32
  if (dbgMode == 1) {
    cmd = "devenv /debugexe model\\Izh_sim_sparse.exe " + toString(argv[5]) + " " + toString(which);
  }
  else {
    cmd = "model\\Izh_sim_sparse.exe " + toString(argv[5]) + " " + toString(which);
  }
#else // UNIX
  if (dbgMode == 1) {
    cmd = "cuda-gdb -tui --args model/Izh_sim_sparse " + toString(argv[5]) + " " + toString(which);
  }
  else {
    cmd = "model/Izh_sim_sparse " + toString(argv[5]) + " " + toString(which);
  }
#endif
  retval=system(cmd.c_str());
  if (retval != 0){
    cerr << "ERROR: Following call failed with status " << retval << ":" << endl << cmd << endl;
    cerr << "Exiting..." << endl;
    exit(1);
  }

  return 0;
}
