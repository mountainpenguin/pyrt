/*
 * $Id: _psutil_linux.h 892 2011-01-13 21:42:53Z g.rodola $
 *
 * LINUX specific module methods for _psutil_linux
 */

#include <Python.h>

static PyObject* linux_ioprio_get(PyObject* self, PyObject* args);
static PyObject* linux_ioprio_set(PyObject* self, PyObject* args);

