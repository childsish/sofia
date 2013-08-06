#include "Python.h"

static PyObject *
interval_interval(PyObject *self, PyObject *args) {
    PyObject *start, *stop = NULL;
    if (!PyArg_UnpackTuple(args, "interval", 1, 2, &start, &stop))
        return NULL;

    PySliceObject *obj = PyObject_New(PySliceObject, &PySlice_Type);

    if (obj == NULL)
        return NULL;

    if (start == NULL) start = Py_None;
    Py_INCREF(start);
    if (stop == NULL) stop = Py_None;
    Py_INCREF(stop);

    obj->step = Py_BuildValue("i", 1);
    obj->start = start;
    obj->stop = stop;

    return (PyObject *) obj; 
}

static PyMethodDef intervalMethods[] = {
    {"interval", interval_interval, METH_VARARGS,
     "Create an interval object"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC initinterval(void) {
    (void) Py_InitModule("interval", intervalMethods);
}

