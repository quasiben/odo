from into.backends.h5py import append, create, resource, discover, convert
from contextlib import contextmanager
from into.utils import tmpfile
from into.chunks import chunks
import datashape
import h5py
import numpy as np


@contextmanager
def file(x):
    with tmpfile('.hdf5') as fn:
        f = h5py.File(fn)
        data = f.create_dataset('/data', data=x, chunks=True,
                                maxshape=(None,) + x.shape[1:])

        try:
            yield fn, f, data
        finally:
            f.close()


x = np.ones((2, 3), dtype='i4')


def test_discover():
    with file(x) as (fn, f, dset):
        assert str(discover(dset)) == str(discover(x))
        assert str(discover(f)) == str(discover({'data': x}))


def eq(a, b):
    c = a == b
    if isinstance(c, np.ndarray):
        c = c.all()
    return c


def test_append():
    with file(x) as (fn, f, dset):
        append(dset, x)
        assert eq(dset[:], np.concatenate([x, x]))


def test_numpy():
    with file(x) as (fn, f, dset):
        assert eq(convert(np.ndarray, dset), x)


def test_chunks():
    with file(x) as (fn, f, dset):
        c = convert(chunks(np.ndarray), dset)
        assert eq(convert(np.ndarray, c), x)


def test_append_chunks():
    with file(x) as (fn, f, dset):
        append(dset, chunks(np.ndarray)([x, x]))

        assert len(dset) == len(x) * 3


def test_create():
    with tmpfile('.hdf5') as fn:
        ds = datashape.dshape('{x: int32, y: {z: 3 * int32}}')
        f = create(h5py.File, dshape='{x: int32, y: {z: 3 * int32}}', path=fn)
        assert isinstance(f, h5py.File)
        assert f.filename == fn
        assert discover(f) == ds
