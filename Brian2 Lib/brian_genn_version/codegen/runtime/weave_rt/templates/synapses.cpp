{% extends 'common_group.cpp' %}

{% block maincode %}
	{# USES_VARIABLES { spiking_synapses} #}
	//// MAIN CODE ////////////
	// scalar code
	const int _vectorisation_idx = 1;
	{{scalar_code|autoindent}}

	for(int _spiking_synapse_idx=0;
		_spiking_synapse_idx<_numspiking_synapses;
		_spiking_synapse_idx++)
	{
	    // vector code
		const int _idx = {{spiking_synapses}}[_spiking_synapse_idx];
		const int _vectorisation_idx = _idx;
        {{vector_code|autoindent}}
	}
{% endblock %}
