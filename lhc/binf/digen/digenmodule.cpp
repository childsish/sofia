#include "Python.h"

#include "digen.h"

static PyObject* digen_generate(PyObject* self, PyObject* args)
{
	PyObject* obj;
	if (!PyArg_ParseTuple(args, "O", &obj))
		return NULL;
	
	int* frq = new int[N_DNUC];
	for (int i = 0; i < N_DNUC; ++i)
	{
		frq[i] = 0;
	}
	
	Py_ssize_t pos = 0;
	PyObject* pkey;
	PyObject* pval;
	while (PyDict_Next(obj, &pos, &pkey, &pval))
	{
		char* ckey = PyString_AsString(pkey);
		int cval = PyInt_AsLong(pval);
		
		int idx = baseToIndex(ckey[0]) * N_BASE + baseToIndex(ckey[1]);
		frq[idx] = cval;
	}
	
	char* cres = generate(frq);
	PyObject* pres = Py_BuildValue("s", cres);
	delete [] cres;
	cres = NULL;
	return pres;
}

static PyMethodDef digenMethods[] = {
	{"generate", digen_generate, METH_VARARGS,
	 "Generate a random string with the given dinucleotide frequencies"},
	{NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC initdigen(void)
{
	(void) Py_InitModule("digen", digenMethods);
}
