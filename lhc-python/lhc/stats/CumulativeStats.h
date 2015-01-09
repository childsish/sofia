#ifndef STATS_H
#define STATS_H

#include <Python.h>

class CumulativeStats {
	public:
	PyObject_HEAD
	/* Type-specific fields go here. */
	int i;
	double avg;
	double ssq;
	
	CumulativeStats();
	
	void append(double val);
	
	double getMean();
	
	double getStd();
};

static PyTypeObject CumulativeStatsType = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "stats.CumulativeStats",/*tp_name*/
    sizeof(CumulativeStats),/*tp_basicsize*/
    0,                         /*tp_itemsize*/
    0,                         /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,        /*tp_flags*/
    "Cumulative Mean and Standard Deviation",/* tp_doc */
};

static PyMethodDef stats_methods[] = {
    {"append", (PyCFunction)CumulativeStats::append, METH}  /* Sentinel */
};

#ifndef PyMODINIT_FUNC	/* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
initstats(void)
{
	PyObject* m;
	
	CumulativeStatsType.tp_new = PyType_GenericNew;
	if (PyType_Ready(&CumulativeStatsType) < 0)
		return;
	
	m = Py_InitModule3("stats", stats_methods,
	 "Basic statical helpers");

	Py_INCREF(&CumulativeStatsType);
	PyModule_AddObject(m, "CumulativeStats", (PyObject *)&CumulativeStatsType);
}


#endif//STATS_H
