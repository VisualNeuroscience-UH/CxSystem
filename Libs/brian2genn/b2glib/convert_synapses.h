
// scalar can be any scalar type such as float, double
#include <stdint.h>
#include <string>
#include <fstream>

#ifndef CONVERT_SYNAPSES
#define CONVERT_SYNAPSES

template<class scalar>
void convert_dynamic_arrays_2_dense_matrix(vector<int32_t> &source, vector<int32_t> &target, vector<scalar> &gvector, scalar *g, int srcNN, int trgNN)
{
    assert(source.size() == target.size());
    assert(source.size() == gvector.size());
    unsigned int size= source.size(); 
    for (int s= 0; s < srcNN; s++) {
	for (int t= 0; t < trgNN; t++) {
	    g[s*trgNN+t]= (scalar) 0.0;
	}
    }
//    cerr << size << "!!!!!!" << endl;
    for (int i= 0; i < size; i++) {
	assert(source[i] < srcNN);
	assert(target[i] < trgNN);
//	cerr << source[i] << " " << target[i] << " " << gvector[i] << endl;
	g[source[i]*trgNN+target[i]]= gvector[i];
    }
//    cerr << endl;
//    cerr << "-------------------------";
}

namespace b2g {
    unsigned int FULL_MONTY= 0;
    unsigned int COPY_ONLY= 1;
};

template<class scalar>
void convert_dynamic_arrays_2_sparse_synapses(vector<int32_t> &source, vector<int32_t> &target, vector<scalar> &gvector, Conductance &c, scalar *gv, int srcNN, int trgNN, unsigned int mode)
{
//    static int convertCnt= 0;
//    string name= "debug_other";
//    name= name+to_string(convertCnt)+".dat";
//    ofstream os(name.c_str());
    // create a list of the postsynaptic targets ordered by presynaptic sources
    static vector<vector<int32_t> > bypre;
    static vector<vector<scalar> > bypreG;
    static unsigned int size;
    if (mode == b2g::FULL_MONTY) {
	assert(source.size() == target.size());
	assert(source.size() == gvector.size());
	bypre.clear();
	bypre.resize(srcNN);
	bypreG.clear();
	bypreG.resize(srcNN);
	size= source.size();
	for (int i= 0; i < size; i++) {
	    assert(source[i] < srcNN);
	    assert(target[i] < trgNN);
	    bypre[source[i]].push_back(target[i]);
	    bypreG[source[i]].push_back(gvector[i]);
	}
	// convert this intermediate representation into the sparse synapses struct
	// assume it has been allocated properly
	unsigned int cnt= 0;
	for (int i= 0; i < srcNN; i++) {
	    size= bypre[i].size();
	    c.indInG[i]= cnt; 
	    for (int j= 0; j < size; j++) {
		c.ind[cnt]= bypre[i][j];
		gv[cnt]= bypreG[i][j];
//		os << i << " " << c.ind[cnt] << " " << gv[cnt] << endl;
		cnt++;
	    }
	}
	c.indInG[srcNN]= cnt;
    }
    else { // COPY_ONLY
	bypreG.clear();
	bypreG.resize(srcNN);
	size= source.size();
	for (int i= 0; i < size; i++) {
	    bypreG[source[i]].push_back(gvector[i]);	    
	}
	unsigned int cnt= 0;
	for (int i= 0; i < srcNN; i++) {
	    size= bypre[i].size();
	    for (int j= 0; j < size; j++) {
		gv[cnt]= bypreG[i][j];
//		os << i << " " << c.ind[cnt] << " " << gv[cnt] << endl;
		cnt++;
	    }
	}
    }
//    convertCnt++;
}

template<class scalar>
void convert_dense_matrix_2_dynamic_arrays(scalar *g, int srcNN, int trgNN, vector<int32_t> &source, vector<int32_t> &target, vector<scalar> &gvector)
{
    assert(source.size() == target.size());
    assert(source.size() == gvector.size());
    unsigned int size= source.size(); 
    for (int i= 0; i < size; i++) {
	assert(source[i] < srcNN);
	assert(target[i] < trgNN);
	gvector[i]= g[source[i]*trgNN+target[i]];
    }
}

template<class scalar>
void convert_sparse_synapses_2_dynamic_arrays(Conductance &c, scalar *gv, int srcNN, int trgNN, vector<int32_t> &source, vector<int32_t> &target, vector<scalar> &gvector, unsigned int mode)
{
//    static int convertCnt= 0;
//    string name= "debug_convert";
//    name= name+to_string(convertCnt)+".dat";
//    ofstream os(name.c_str());
// note: this does not preserve the original order of entries in the brian arrays - is that a problem?
    if (mode == b2g::FULL_MONTY) {
	assert(source.size() == target.size());
	assert(source.size() == gvector.size());
	unsigned int size= source.size();
	unsigned int cnt= 0;
	for (int i= 0; i < srcNN; i++) {
	    for (int j= c.indInG[i]; j < c.indInG[i+1]; j++) {
		source[cnt]= i;
		target[cnt]= c.ind[j];
		gvector[cnt]= gv[j];
//		os << source[cnt] << " " << target[cnt] << " " << gvector[cnt] << endl;
		cnt++;
	    }
	}
    }
    else {
	unsigned int size= source.size();
	unsigned int cnt= 0;
	for (int i= 0; i < srcNN; i++) {
	    for (int j= c.indInG[i]; j < c.indInG[i+1]; j++) {
		gvector[cnt++]= gv[j];
	    }
	}
    }
//    os.close();
//    convertCnt++;
}	

void create_hidden_weightmatrix(vector<int32_t> &source, vector<int32_t> &target, char* hwm, int srcNN, int trgNN)
{
    for (int s= 0; s < srcNN; s++) {
	for (int t= 0; t < trgNN; t++) {
	    hwm[s*trgNN+t]= 0;
	}
    }
    for (int i= 0; i < source.size(); i++) {
	hwm[source[i]*trgNN+target[i]]= 1;
    }
}
#endif
