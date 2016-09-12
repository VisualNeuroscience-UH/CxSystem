{% extends 'common_group.cpp' %}

{% block maincode %}
    {#
    USES_VARIABLES { _synaptic_pre, _synaptic_post, rand,
                     N_incoming, N_outgoing, N,
                     N_pre, N_post, _source_offset, _target_offset}
    #}
    {# WRITES_TO_READ_ONLY_VARIABLES { _synaptic_pre, _synaptic_post,
                      N_incoming, N_outgoing, N}
    #}
    srand((unsigned int)time(NULL));
    const int _buffer_size = 1024;
    int *const _prebuf = new int[_buffer_size];
    int *const _postbuf = new int[_buffer_size];
    int _curbuf = 0;

    // Resize N_incoming and N_outgoing according to the size of the
    // source/target groups
    PyObject_CallMethod(_var_N_incoming, "resize", "i", {{constant_or_scalar('N_post', variables['N_post'])}} + _target_offset);
    PyObject_CallMethod(_var_N_outgoing, "resize", "i", {{constant_or_scalar('N_pre', variables['N_pre'])}} + _source_offset);
    int *_N_incoming = (int *)(((PyArrayObject*)(PyObject*){{_dynamic_N_incoming}}.attr("data"))->data);
    int *_N_outgoing = (int *)(((PyArrayObject*)(PyObject*){{_dynamic_N_outgoing}}.attr("data"))->data);
    // scalar code
	const int _vectorisation_idx = 1;
	{{scalar_code|autoindent}}

    for(int _i=0; _i<_num_all_pre; _i++)
    {
        for(int _j=0; _j<_num_all_post; _j++)
        {
            const int _vectorisation_idx = _j;
            {# The abstract code consists of the following lines (the first two lines
            are there to properly support subgroups as sources/targets):
            _pre_idx = _all_pre
            _post_idx = _all_post
            _cond = {user-specified condition}
            _n = {user-specified number of synapses}
            _p = {user-specified probability}
            #}
            // vector code
            {{ super() }}
            // Add to buffer
            if(_cond)
            {
                if (_p != 1.0) {
                    // We have to use _rand instead of rand to use our rand
                    // function, not the one from the C standard library
                    if (_rand(_vectorisation_idx) >= _p)
                        continue;
                }

                for (int _repetition=0; _repetition<_n; _repetition++) {
                    _N_outgoing[_pre_idx] += 1;
                    _N_incoming[_post_idx] += 1;
                    _prebuf[_curbuf] = _pre_idx;
                    _postbuf[_curbuf] = _post_idx;
                    _curbuf++;
                    // Flush buffer
                    if(_curbuf==_buffer_size)
                    {
                        _flush_buffer(_prebuf, {{_dynamic__synaptic_pre}}, _curbuf);
                        _flush_buffer(_postbuf, {{_dynamic__synaptic_post}}, _curbuf);
                        _curbuf = 0;
                    }
                }
            }
        }
    }
    // Final buffer flush
    _flush_buffer(_prebuf, {{_dynamic__synaptic_pre}}, _curbuf);
    _flush_buffer(_postbuf, {{_dynamic__synaptic_post}}, _curbuf);

    const int newsize = {{_dynamic__synaptic_pre}}.size();
    // now we need to resize all registered variables and set the total number
    // of synapses (via Python)
    py::tuple _newlen_tuple(1);
    _newlen_tuple[0] = newsize;
    _owner.mcall("_resize", _newlen_tuple);
    delete [] _prebuf;
    delete [] _postbuf;
{% endblock %}

{% block support_code_block %}
// Flush a buffered segment into a dynamic array
void _flush_buffer(int *buf, py::object &dynarr, int N)
{
    int _curlen = dynarr.attr("shape")[0];
    int _newlen = _curlen+N;
    // Resize the array
    py::tuple _newlen_tuple(1);
    _newlen_tuple[0] = _newlen;
    dynarr.mcall("resize", _newlen_tuple);
    // Get the potentially newly created underlying data arrays
    int *data = (int*)(((PyArrayObject*)(PyObject*)dynarr.attr("data"))->data);
    // Copy the values across
    for(int i=0; i<N; i++)
    {
        data[_curlen+i] = buf[i];
    }
}

{{ super() }}

{% endblock %}
