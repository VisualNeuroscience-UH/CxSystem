
  GPU enhanced Neuronal Network (GeNN)
  ====================================

GeNN is a GPU enhanced Neuronal Network simulation environment based on code
generation for Nvidia CUDA.


  [1] INSTALLING GeNN
  ===================

    [1.1] WINDOWS INSTALL
    ---------------------

(1) Download and unpack GeNN.zip to a convenient location, then download and
    install the Microsoft Visual C++ compiler and IDE from:
      http://www.visualstudio.com/en-us/downloads
    then download and install the Nvidia CUDA toolkit from: 
      https://developer.nvidia.com/cuda-downloads

(2) Ensure that the "CUDA_PATH" environment variable is defined, and points
    to the location of the Nvidia CUDA toolkit installation, by using:
      ECHO %CUDA_PATH%
    This variable is usully set during most CUDA installations on Windows
    systems. if not, correct this using:
      SETX CUDA_PATH "[drive]\Program Files\NVIDIA GPU Computing Toolkit\CUDA\[version]"

(3) Define the environment variable "GENN_PATH" to point to the directory
    in which GeNN was located. For example, use:
      SETX GENN_PATH "\path\to\genn\"

(4) Add "%GENN_PATH%\lib\bin" to your %PATH% variable. For example, use:
      SETX PATH "%GENN_PATH%\lib\bin;%PATH%"

(5) Define VC_PATH as the path to your most recent Visual Studio
installation, e.g.
setx VC_PATH "C:\Program Files (x86)\Microsoft Visual Studio 10.0"

Alternatively you can do one of the following:

  i) Run the vscvsrsall.bat script under Visual C++ directory before
  projects are compiled and run in a given cmd.exe terminal window.

  ii) Alternatively, one can use the shortcut link in:
    start menu -> all programs -> Microsoft Visual Studio ->
    Visual Studio Tools -> Visual Studio Command Prompt
  which will launch an instance of cmd.exe in which the vcvarsall.bat compiler
  setup script has already been executed.

This completes the installation.

NOTE:

    [1.2] LINUX / MAC INSTALL
    -------------------------

(1) Unpack GeNN.zip in a convenient location, then download and install the
    Nvidia CUDA toolkit from:
      https://developer.nvidia.com/cuda-downloads
    and install the GNU GCC compiler collection and GNU Make build environment
    if it is not already present on the system.

(2) Set the environment variable "CUDA_PATH" to the location of your Nvidia
    CUDA toolkit installation. For example, if your CUDA toolkit was installed
    to "/usr/local/cuda", you can use:
      echo "export CUDA_PATH=/usr/local/cuda" >> ~/.bash_profile

(3) Set the environment variable "GENN_PATH" to point to the extracted GeNN 
    directory. For example, if you extracted GeNN to "/home/me/genn", then you
    can use:
      echo "export GENN_PATH=/home/me/genn" >> ~/.bash_profile

(4) Add "$GENN_PATH/lib/bin" to your $PATH variable. For example, you can use:
      echo "export PATH=$PATH:$GENN_PATH/lib/bin" >> ~/.bash_profile

This completes the installation.


  [2] USING GeNN
  ==============

    [2.1] SAMPLE PROJECTS
    ---------------------

At the moment, the following example projects are provided with GeNN:

1: Locust olfactory system example (Nowotny et al. 2005):
2: Izhikevich network receiving Poisson input spike trains:
3: Single compartment Izhikevich neuron(s)
4: Pulse-coupled Izhikevich network
5: Izhikevich network with delayed synapses

In order to get a quick start and run one of the the provided example models,
navigate to one of the example project directories in $GENN_PATH/userproject/,
and then follow the instructions in the README file contained within.

DEBUGGING:
  The last argument to "generate_run" helper binary, or similar file, enables
  the debugging flags while compiling generateAll.cc under lib/src/ and *.cu
  under individual user project directory, and will run the corresponding
  executables with cuda-gdb consecutively. If you want to skip one of these
  debugging steps, simply press r while on the debugging screen.


    [2.2] SIMULATING A NEW MODEL
    ----------------------------

The sample projects listed above are already quite highly integrated
examples. If one was to use the library for GPU code generation of their
own model, the following would be done:

a) The model in question is defined in a file, say "Model1.cc".  

b) this file needs to 
  (i) define "DT" 
  (ii) include "modelSpec.h" and "modelSpec.cc"
  (iii) contains the model's definition in the form of a function 
  "void modelDefinition(NNmodel &model)" 
  ("MBody1.cc") shows a typical example)

c) The programmer defines their own modeling code along similar lines as
"map_classol.*" together with "classol_sim.*", etcetera. In this code, 

  - they define the connectivity matrices between neuron groups. (In the
    example here those are read from files).  

  - they define input patterns (e.g. for Poisson neurons like in the
    example) 

  - they use "stepTimeGPU(x, y, z);" to run one time step on the GPU or
    "stepTimeCPU(x, y, z);" to run one on the CPU. (both versions are
    always compiled). However, mixing the two does not make too much
    sense. The host version uses the same memory whereto results from the
    GPU version are copied (see next point) 

  - they use functions like "copyStateFromDevice();" etcetera to obtain
    results from GPU calculations.

  - the simulation code is then produced in the following two steps:
    "buildmodel.[sh/bat] Model1 [DEBUG OFF/ON]" and "make clean && make"
