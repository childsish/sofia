#include <Python.h>
#include "structmember.h"

typedef struct {
	PyObject_HEAD
	int f;
	int t;
} Range;

static PyObject*
Range_new(PyTypeObject* type, PyObject* args, PyObject* kwargs) {
	Range* self;
	
	self = (Range*)type->tp_alloc(type, 0);
	if (self != NULL) {
		self->f = 0;
		self->t = 0;
    }

    return (PyObject *)self;
}

static int
Range_init(Range* self, PyObject* args, PyObject* kwargs) {
	static char *kwlist[] = {"f", "t", NULL};
	if (!PyArg_ParseTupleAndKeywords(args, kwargs, "ii", kwlist,
	 &self->f, &self->t))
		return -1;
	return 0;
}

static PyMemberDef Range_members[] = {
	{"f", T_INT, offsetof(Range, f), 0, "from"},
	{"t", T_INT, offsetof(Range, t), 0, "to"}
	{NULL} /* Sentinel */
};

static PyTypeObject RangeType = {
	PyObject_HEAD_INIT(NULL)
	0,                         /*ob_size*/
	"range.Range",             /*tp_name*/
	sizeof(Range),             /*tp_basicsize*/
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
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
	"Range objects",           /* tp_doc */
	0,                         /* tp_traverse */
	0,                         /* tp_clear */
	0,                         /* tp_richcompare */
	0,                         /* tp_weaklistoffset */
	0,                         /* tp_iter */
	0,                         /* tp_iternext */
	Range_methods,             /* tp_methods */
	Range_members,             /* tp_members */
	Range_getseters,           /* tp_getset */
	0,                         /* tp_base */
	0,                         /* tp_dict */
	0,                         /* tp_descr_get */
	0,                         /* tp_descr_set */
	0,                         /* tp_dictoffset */
	(initproc)Range_init,      /* tp_init */
	0,                         /* tp_alloc */
	Range_new,                 /* tp_new */
};

static PyObject*
Range_overlaps(Range* self, PyObject* args, PyObject* kwargs) {
	static char *kwlist[] = {"other", NULL};
	PyObject* other;
	if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O!", kwlist,
	 &RangeType, &other))
		return -1;
	
	
}

static PyMethodDef range_methods[] = {
	{"overlaps", (PyCFunction)Range_overlaps, METH_KEYWORDS,
	 "Does this range overlap with the other?"},
	{NULL}  /* Sentinel */
};

#ifndef PyMODINIT_FUNC
#define PyMODINIT_FUNC void
#endif

PyMODINIT_FUNC initrange(void) {
	PyObject* m;
	
	RangeType.tp_new = PyType_GenericNew;
	if (PyType_Ready(&RangeType) < 0)
		return;
	
	m = Py_InitModule3("range", range_methods,
					   "Range and SuperRange class for superior slicing");
	
	Py_INCREF(&RangeType);
	PyModule_AddObject(m, "Range", (PyObject*) &RangeType);
}
