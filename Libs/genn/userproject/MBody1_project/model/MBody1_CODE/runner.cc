

//-------------------------------------------------------------------------
/*! \file runner.cc

\brief File generated from GeNN for the model MBody1 containing general control code.
*/
//-------------------------------------------------------------------------

#include <cstdio>
#include <cassert>
#include <stdint.h>
#include "utils.h"

#include "numlib/simpleBit.h"

#define RUNNER_CC_COMPILE
#include "definitions.h"

#ifndef scalar
typedef float scalar;
#endif
#ifndef SCALAR_MIN
#define SCALAR_MIN 1.17549e-38f
#endif
#ifndef SCALAR_MAX
#define SCALAR_MAX 3.40282e+38f
#endif
#define Conductance SparseProjection
/*struct Conductance is deprecated. 
  By GeNN 2.0, Conductance is renamed as SparseProjection and contains only indexing values. 
  Please consider updating your user code by renaming Conductance as SparseProjection 
  and making g member a synapse variable.*/
#ifndef MYRAND
#define MYRAND(Y,X) Y = Y * 1103515245 + 12345; X = (Y >> 16);
#endif

#ifndef MYRAND_MAX
#define MYRAND_MAX 0x0000FFFFFFFFFFFFLL
#endif
#ifndef CHECK_CUDA_ERRORS
#define CHECK_CUDA_ERRORS(call) {\
    cudaError_t error = call;\
    if (error != cudaSuccess) {\
        fprintf(stderr, "%s: %i: cuda error %i: %s\n", __FILE__, __LINE__, (int) error, cudaGetErrorString(error));\
        exit(EXIT_FAILURE);\
    }\
}
#endif

template<class T>
void deviceMemAllocate(T* hostPtr, const T &devSymbol, size_t size)
{
    void *devptr;
    CHECK_CUDA_ERRORS(cudaMalloc(hostPtr, size));
    CHECK_CUDA_ERRORS(cudaGetSymbolAddress(&devptr, devSymbol));
    CHECK_CUDA_ERRORS(cudaMemcpy(devptr, hostPtr, sizeof(void*), cudaMemcpyHostToDevice));
}

//-------------------------------------------------------------------------
/*! \brief Function to convert a firing probability (per time step) 
to an integer of type uint64_t that can be used as a threshold for the GeNN random number generator to generate events with the given probability.
*/
//-------------------------------------------------------------------------

void convertProbabilityToRandomNumberThreshold(float *p_pattern, uint64_t *pattern, int N)
{
    float fac= pow(2.0, (double) sizeof(uint64_t)*8-16);
    for (int i= 0; i < N; i++) {
        pattern[i]= (uint64_t) (p_pattern[i]*fac);
    }
}

//-------------------------------------------------------------------------
/*! \brief Function to convert a firing rate (in kHz) 
to an integer of type uint64_t that can be used as a threshold for the GeNN random number generator to generate events with the given rate.
*/
//-------------------------------------------------------------------------

void convertRateToRandomNumberThreshold(float *rateKHz_pattern, uint64_t *pattern, int N)
{
    float fac= pow(2.0, (double) sizeof(uint64_t)*8-16)*DT;
    for (int i= 0; i < N; i++) {
        pattern[i]= (uint64_t) (rateKHz_pattern[i]*fac);
    }
}

// global variables
unsigned long long iT= 0;
float t;
// neuron variables
__device__ volatile unsigned int d_done;
unsigned int * glbSpkCntPN;
unsigned int * d_glbSpkCntPN;
__device__ unsigned int * dd_glbSpkCntPN;
unsigned int * glbSpkPN;
unsigned int * d_glbSpkPN;
__device__ unsigned int * dd_glbSpkPN;
float * sTPN;
float * d_sTPN;
__device__ float * dd_sTPN;
float * VPN;
float * d_VPN;
__device__ float * dd_VPN;
uint64_t * seedPN;
uint64_t * d_seedPN;
__device__ uint64_t * dd_seedPN;
float * spikeTimePN;
float * d_spikeTimePN;
__device__ float * dd_spikeTimePN;
unsigned int * glbSpkCntKC;
unsigned int * d_glbSpkCntKC;
__device__ unsigned int * dd_glbSpkCntKC;
unsigned int * glbSpkKC;
unsigned int * d_glbSpkKC;
__device__ unsigned int * dd_glbSpkKC;
float * sTKC;
float * d_sTKC;
__device__ float * dd_sTKC;
float * VKC;
float * d_VKC;
__device__ float * dd_VKC;
float * mKC;
float * d_mKC;
__device__ float * dd_mKC;
float * hKC;
float * d_hKC;
__device__ float * dd_hKC;
float * nKC;
float * d_nKC;
__device__ float * dd_nKC;
unsigned int * glbSpkCntLHI;
unsigned int * d_glbSpkCntLHI;
__device__ unsigned int * dd_glbSpkCntLHI;
unsigned int * glbSpkLHI;
unsigned int * d_glbSpkLHI;
__device__ unsigned int * dd_glbSpkLHI;
unsigned int * glbSpkCntEvntLHI;
unsigned int * d_glbSpkCntEvntLHI;
__device__ unsigned int * dd_glbSpkCntEvntLHI;
unsigned int * glbSpkEvntLHI;
unsigned int * d_glbSpkEvntLHI;
__device__ unsigned int * dd_glbSpkEvntLHI;
float * sTLHI;
float * d_sTLHI;
__device__ float * dd_sTLHI;
float * VLHI;
float * d_VLHI;
__device__ float * dd_VLHI;
float * mLHI;
float * d_mLHI;
__device__ float * dd_mLHI;
float * hLHI;
float * d_hLHI;
__device__ float * dd_hLHI;
float * nLHI;
float * d_nLHI;
__device__ float * dd_nLHI;
unsigned int * glbSpkCntDN;
unsigned int * d_glbSpkCntDN;
__device__ unsigned int * dd_glbSpkCntDN;
unsigned int * glbSpkDN;
unsigned int * d_glbSpkDN;
__device__ unsigned int * dd_glbSpkDN;
unsigned int * glbSpkCntEvntDN;
unsigned int * d_glbSpkCntEvntDN;
__device__ unsigned int * dd_glbSpkCntEvntDN;
unsigned int * glbSpkEvntDN;
unsigned int * d_glbSpkEvntDN;
__device__ unsigned int * dd_glbSpkEvntDN;
float * sTDN;
float * d_sTDN;
__device__ float * dd_sTDN;
float * VDN;
float * d_VDN;
__device__ float * dd_VDN;
float * mDN;
float * d_mDN;
__device__ float * dd_mDN;
float * hDN;
float * d_hDN;
__device__ float * dd_hDN;
float * nDN;
float * d_nDN;
__device__ float * dd_nDN;

// synapse variables
float * inSynPNKC;
float * d_inSynPNKC;
__device__ float * dd_inSynPNKC;
float * gPNKC;
float * d_gPNKC;
__device__ float * dd_gPNKC;
float * inSynPNLHI;
float * d_inSynPNLHI;
__device__ float * dd_inSynPNLHI;
float * gPNLHI;
float * d_gPNLHI;
__device__ float * dd_gPNLHI;
float * inSynLHIKC;
float * d_inSynLHIKC;
__device__ float * dd_inSynLHIKC;
float * inSynKCDN;
float * d_inSynKCDN;
__device__ float * dd_inSynKCDN;
float * gKCDN;
float * d_gKCDN;
__device__ float * dd_gKCDN;
float * gRawKCDN;
float * d_gRawKCDN;
__device__ float * dd_gRawKCDN;
float * inSynDNDN;
float * d_inSynDNDN;
__device__ float * dd_inSynDNDN;

 // memory space that holds the kernel arguments/parameters
char kernelPara[16];
void *d_kernelPara;
__device__ char dd_kernelPara[16];
uint64_t * &ratesPN= *((uint64_t * *)(kernelPara+0));
__device__ uint64_t * &dd_ratesPN= *((uint64_t * *)(dd_kernelPara+0));
unsigned int &offsetPN= *((unsigned int *)(kernelPara+8));
__device__ unsigned int &dd_offsetPN= *((unsigned int *)(dd_kernelPara+8));


#include "sparseUtils.cc"

#include "runnerGPU.cc"

#include "neuronFnct.cc"
#include "synapseFnct.cc"
void allocateMem()
{
    CHECK_CUDA_ERRORS(cudaSetDevice(0));
    glbSpkCntPN = new unsigned int[1];
    deviceMemAllocate(&d_glbSpkCntPN, dd_glbSpkCntPN, 1 * sizeof(unsigned int));
    glbSpkPN = new unsigned int[100];
    deviceMemAllocate(&d_glbSpkPN, dd_glbSpkPN, 100 * sizeof(unsigned int));
    sTPN = new float[100];
    deviceMemAllocate(&d_sTPN, dd_sTPN, 100 * sizeof(float));
    VPN = new float[100];
    deviceMemAllocate(&d_VPN, dd_VPN, 100 * sizeof(float));
    seedPN = new uint64_t[100];
    deviceMemAllocate(&d_seedPN, dd_seedPN, 100 * sizeof(uint64_t));
    spikeTimePN = new float[100];
    deviceMemAllocate(&d_spikeTimePN, dd_spikeTimePN, 100 * sizeof(float));

    glbSpkCntKC = new unsigned int[1];
    deviceMemAllocate(&d_glbSpkCntKC, dd_glbSpkCntKC, 1 * sizeof(unsigned int));
    glbSpkKC = new unsigned int[1000];
    deviceMemAllocate(&d_glbSpkKC, dd_glbSpkKC, 1000 * sizeof(unsigned int));
    sTKC = new float[1000];
    deviceMemAllocate(&d_sTKC, dd_sTKC, 1000 * sizeof(float));
    VKC = new float[1000];
    deviceMemAllocate(&d_VKC, dd_VKC, 1000 * sizeof(float));
    mKC = new float[1000];
    deviceMemAllocate(&d_mKC, dd_mKC, 1000 * sizeof(float));
    hKC = new float[1000];
    deviceMemAllocate(&d_hKC, dd_hKC, 1000 * sizeof(float));
    nKC = new float[1000];
    deviceMemAllocate(&d_nKC, dd_nKC, 1000 * sizeof(float));

    glbSpkCntLHI = new unsigned int[1];
    deviceMemAllocate(&d_glbSpkCntLHI, dd_glbSpkCntLHI, 1 * sizeof(unsigned int));
    glbSpkLHI = new unsigned int[20];
    deviceMemAllocate(&d_glbSpkLHI, dd_glbSpkLHI, 20 * sizeof(unsigned int));
    glbSpkCntEvntLHI = new unsigned int[1];
    deviceMemAllocate(&d_glbSpkCntEvntLHI, dd_glbSpkCntEvntLHI, 1 * sizeof(unsigned int));
    glbSpkEvntLHI = new unsigned int[20];
    deviceMemAllocate(&d_glbSpkEvntLHI, dd_glbSpkEvntLHI, 20 * sizeof(unsigned int));
    sTLHI = new float[20];
    deviceMemAllocate(&d_sTLHI, dd_sTLHI, 20 * sizeof(float));
    VLHI = new float[20];
    deviceMemAllocate(&d_VLHI, dd_VLHI, 20 * sizeof(float));
    mLHI = new float[20];
    deviceMemAllocate(&d_mLHI, dd_mLHI, 20 * sizeof(float));
    hLHI = new float[20];
    deviceMemAllocate(&d_hLHI, dd_hLHI, 20 * sizeof(float));
    nLHI = new float[20];
    deviceMemAllocate(&d_nLHI, dd_nLHI, 20 * sizeof(float));

    glbSpkCntDN = new unsigned int[1];
    deviceMemAllocate(&d_glbSpkCntDN, dd_glbSpkCntDN, 1 * sizeof(unsigned int));
    glbSpkDN = new unsigned int[100];
    deviceMemAllocate(&d_glbSpkDN, dd_glbSpkDN, 100 * sizeof(unsigned int));
    glbSpkCntEvntDN = new unsigned int[1];
    deviceMemAllocate(&d_glbSpkCntEvntDN, dd_glbSpkCntEvntDN, 1 * sizeof(unsigned int));
    glbSpkEvntDN = new unsigned int[100];
    deviceMemAllocate(&d_glbSpkEvntDN, dd_glbSpkEvntDN, 100 * sizeof(unsigned int));
    sTDN = new float[100];
    deviceMemAllocate(&d_sTDN, dd_sTDN, 100 * sizeof(float));
    VDN = new float[100];
    deviceMemAllocate(&d_VDN, dd_VDN, 100 * sizeof(float));
    mDN = new float[100];
    deviceMemAllocate(&d_mDN, dd_mDN, 100 * sizeof(float));
    hDN = new float[100];
    deviceMemAllocate(&d_hDN, dd_hDN, 100 * sizeof(float));
    nDN = new float[100];
    deviceMemAllocate(&d_nDN, dd_nDN, 100 * sizeof(float));

    inSynPNKC = new float[1000];
    deviceMemAllocate(&d_inSynPNKC, dd_inSynPNKC, 1000 * sizeof(float));
    gPNKC = new float[100000];
    deviceMemAllocate(&d_gPNKC, dd_gPNKC, 100000 * sizeof(float));

    inSynPNLHI = new float[20];
    deviceMemAllocate(&d_inSynPNLHI, dd_inSynPNLHI, 20 * sizeof(float));
    gPNLHI = new float[2000];
    deviceMemAllocate(&d_gPNLHI, dd_gPNLHI, 2000 * sizeof(float));

    inSynLHIKC = new float[1000];
    deviceMemAllocate(&d_inSynLHIKC, dd_inSynLHIKC, 1000 * sizeof(float));

    inSynKCDN = new float[100];
    deviceMemAllocate(&d_inSynKCDN, dd_inSynKCDN, 100 * sizeof(float));
    gKCDN = new float[100000];
    deviceMemAllocate(&d_gKCDN, dd_gKCDN, 100000 * sizeof(float));
    gRawKCDN = new float[100000];
    deviceMemAllocate(&d_gRawKCDN, dd_gRawKCDN, 100000 * sizeof(float));

    inSynDNDN = new float[100];
    deviceMemAllocate(&d_inSynDNDN, dd_inSynDNDN, 100 * sizeof(float));

// Make the connection where to copy kernel arguments/parameters
CHECK_CUDA_ERRORS(cudaGetSymbolAddress((void **) &d_kernelPara, dd_kernelPara));
}

//-------------------------------------------------------------------------
/*! \brief Function to (re)set all model variables to their compile-time, homogeneous initial values.
 Note that this typically includes synaptic weight values. The function (re)sets host side variables and copies them to the GPU device.
*/
//-------------------------------------------------------------------------

void initialize()
{
    srand((unsigned int) 1234);

    // neuron variables
    glbSpkCntPN[0] = 0;
    for (int i = 0; i < 100; i++) {
        glbSpkPN[i] = 0;
    }
    for (int i = 0; i < 100; i++) {
        sTPN[i] = -10.0;
    }
    for (int i = 0; i < 100; i++) {
        VPN[i] = -60.0000f;
    }
    for (int i = 0; i < 100; i++) {
        seedPN[i] = 0.00000f;
    }
    for (int i = 0; i < 100; i++) {
        spikeTimePN[i] = -10.0000f;
    }
    for (int i = 0; i < 100; i++) {
        seedPN[i] = rand();
    }
    glbSpkCntKC[0] = 0;
    for (int i = 0; i < 1000; i++) {
        glbSpkKC[i] = 0;
    }
    for (int i = 0; i < 1000; i++) {
        sTKC[i] = -10.0;
    }
    for (int i = 0; i < 1000; i++) {
        VKC[i] = -60.0000f;
    }
    for (int i = 0; i < 1000; i++) {
        mKC[i] = 0.0529324f;
    }
    for (int i = 0; i < 1000; i++) {
        hKC[i] = 0.317677f;
    }
    for (int i = 0; i < 1000; i++) {
        nKC[i] = 0.596121f;
    }
    glbSpkCntLHI[0] = 0;
    for (int i = 0; i < 20; i++) {
        glbSpkLHI[i] = 0;
    }
    glbSpkCntEvntLHI[0] = 0;
    for (int i = 0; i < 20; i++) {
        glbSpkEvntLHI[i] = 0;
    }
    for (int i = 0; i < 20; i++) {
        sTLHI[i] = -10.0;
    }
    for (int i = 0; i < 20; i++) {
        VLHI[i] = -60.0000f;
    }
    for (int i = 0; i < 20; i++) {
        mLHI[i] = 0.0529324f;
    }
    for (int i = 0; i < 20; i++) {
        hLHI[i] = 0.317677f;
    }
    for (int i = 0; i < 20; i++) {
        nLHI[i] = 0.596121f;
    }
    glbSpkCntDN[0] = 0;
    for (int i = 0; i < 100; i++) {
        glbSpkDN[i] = 0;
    }
    glbSpkCntEvntDN[0] = 0;
    for (int i = 0; i < 100; i++) {
        glbSpkEvntDN[i] = 0;
    }
    for (int i = 0; i < 100; i++) {
        sTDN[i] = -10.0;
    }
    for (int i = 0; i < 100; i++) {
        VDN[i] = -60.0000f;
    }
    for (int i = 0; i < 100; i++) {
        mDN[i] = 0.0529324f;
    }
    for (int i = 0; i < 100; i++) {
        hDN[i] = 0.317677f;
    }
    for (int i = 0; i < 100; i++) {
        nDN[i] = 0.596121f;
    }

    // synapse variables
    for (int i = 0; i < 1000; i++) {
        inSynPNKC[i] = 0.00000f;
    }
    for (int i = 0; i < 100000; i++) {
        gPNKC[i] = 0.0100000f;
    }
    for (int i = 0; i < 20; i++) {
        inSynPNLHI[i] = 0.00000f;
    }
    for (int i = 0; i < 2000; i++) {
        gPNLHI[i] = 0.00000f;
    }
    for (int i = 0; i < 1000; i++) {
        inSynLHIKC[i] = 0.00000f;
    }
    for (int i = 0; i < 100; i++) {
        inSynKCDN[i] = 0.00000f;
    }
    for (int i = 0; i < 100000; i++) {
        gKCDN[i] = 0.0100000f;
    }
    for (int i = 0; i < 100000; i++) {
        gRawKCDN[i] = 0.0100000f;
    }
    for (int i = 0; i < 100; i++) {
        inSynDNDN[i] = 0.00000f;
    }


    copyStateToDevice();

    //initializeAllSparseArrays(); //I comment this out instead of removing to keep in mind that sparse arrays need to be initialised manually by hand later
}

void initializeAllSparseArrays() {
}

void initMBody1()
 {
    
}

    void freeMem()
{
    delete[] glbSpkCntPN;
    CHECK_CUDA_ERRORS(cudaFree(d_glbSpkCntPN));
    delete[] glbSpkPN;
    CHECK_CUDA_ERRORS(cudaFree(d_glbSpkPN));
    delete[] sTPN;
    CHECK_CUDA_ERRORS(cudaFree(d_sTPN));
    delete[] VPN;
    CHECK_CUDA_ERRORS(cudaFree(d_VPN));
    delete[] seedPN;
    CHECK_CUDA_ERRORS(cudaFree(d_seedPN));
    delete[] spikeTimePN;
    CHECK_CUDA_ERRORS(cudaFree(d_spikeTimePN));
    delete[] glbSpkCntKC;
    CHECK_CUDA_ERRORS(cudaFree(d_glbSpkCntKC));
    delete[] glbSpkKC;
    CHECK_CUDA_ERRORS(cudaFree(d_glbSpkKC));
    delete[] sTKC;
    CHECK_CUDA_ERRORS(cudaFree(d_sTKC));
    delete[] VKC;
    CHECK_CUDA_ERRORS(cudaFree(d_VKC));
    delete[] mKC;
    CHECK_CUDA_ERRORS(cudaFree(d_mKC));
    delete[] hKC;
    CHECK_CUDA_ERRORS(cudaFree(d_hKC));
    delete[] nKC;
    CHECK_CUDA_ERRORS(cudaFree(d_nKC));
    delete[] glbSpkCntLHI;
    CHECK_CUDA_ERRORS(cudaFree(d_glbSpkCntLHI));
    delete[] glbSpkLHI;
    CHECK_CUDA_ERRORS(cudaFree(d_glbSpkLHI));
    delete[] glbSpkCntEvntLHI;
    CHECK_CUDA_ERRORS(cudaFree(d_glbSpkCntEvntLHI));
    delete[] glbSpkEvntLHI;
    CHECK_CUDA_ERRORS(cudaFree(d_glbSpkEvntLHI));
    delete[] sTLHI;
    CHECK_CUDA_ERRORS(cudaFree(d_sTLHI));
    delete[] VLHI;
    CHECK_CUDA_ERRORS(cudaFree(d_VLHI));
    delete[] mLHI;
    CHECK_CUDA_ERRORS(cudaFree(d_mLHI));
    delete[] hLHI;
    CHECK_CUDA_ERRORS(cudaFree(d_hLHI));
    delete[] nLHI;
    CHECK_CUDA_ERRORS(cudaFree(d_nLHI));
    delete[] glbSpkCntDN;
    CHECK_CUDA_ERRORS(cudaFree(d_glbSpkCntDN));
    delete[] glbSpkDN;
    CHECK_CUDA_ERRORS(cudaFree(d_glbSpkDN));
    delete[] glbSpkCntEvntDN;
    CHECK_CUDA_ERRORS(cudaFree(d_glbSpkCntEvntDN));
    delete[] glbSpkEvntDN;
    CHECK_CUDA_ERRORS(cudaFree(d_glbSpkEvntDN));
    delete[] sTDN;
    CHECK_CUDA_ERRORS(cudaFree(d_sTDN));
    delete[] VDN;
    CHECK_CUDA_ERRORS(cudaFree(d_VDN));
    delete[] mDN;
    CHECK_CUDA_ERRORS(cudaFree(d_mDN));
    delete[] hDN;
    CHECK_CUDA_ERRORS(cudaFree(d_hDN));
    delete[] nDN;
    CHECK_CUDA_ERRORS(cudaFree(d_nDN));
    delete[] inSynPNKC;
    CHECK_CUDA_ERRORS(cudaFree(d_inSynPNKC));
    delete[] gPNKC;
    CHECK_CUDA_ERRORS(cudaFree(d_gPNKC));
    delete[] inSynPNLHI;
    CHECK_CUDA_ERRORS(cudaFree(d_inSynPNLHI));
    delete[] gPNLHI;
    CHECK_CUDA_ERRORS(cudaFree(d_gPNLHI));
    delete[] inSynLHIKC;
    CHECK_CUDA_ERRORS(cudaFree(d_inSynLHIKC));
    delete[] inSynKCDN;
    CHECK_CUDA_ERRORS(cudaFree(d_inSynKCDN));
    delete[] gKCDN;
    CHECK_CUDA_ERRORS(cudaFree(d_gKCDN));
    delete[] gRawKCDN;
    CHECK_CUDA_ERRORS(cudaFree(d_gRawKCDN));
    delete[] inSynDNDN;
    CHECK_CUDA_ERRORS(cudaFree(d_inSynDNDN));
}

void exitGeNN(){
  freeMem();
  cudaDeviceReset();
}
// ------------------------------------------------------------------------
// Throw an error for "old style" time stepping calls
template <class T>
void stepTimeCPU(T arg1, ...)
 {
    
gennError("Since GeNN 2.2 the call to step time has changed to not take any arguments. You appear to attempt to pass arguments. This is no longer supported. See the GeNN 2.2. release notes and the manual for examples how to pass data like, e.g., Poisson rates and direct inputs, that were previously handled through arguments.");
    }

// ------------------------------------------------------------------------
// the actual time stepping procedure
void stepTimeCPU()
{
        calcSynapsesCPU(t);
        learnSynapsesPostHost(t);
    calcNeuronsCPU(t);
iT++;
t= iT*DT;
}
