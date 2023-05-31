import os
import numpy as np
from tvb.simulator.lab import connectivity
import tempfile
from zipfile import ZipFile

data_root = os.path.abspath(
        os.path.join(
            os.path.dirname(
                os.path.dirname(
                    os.path.dirname(__file__)
                ),
            ),
            'data'
        )
)

def path(relp):
    return os.path.join(data_root, os.path.normpath(relp))


def save_conn_to_zip(filename:os.PathLike, conn: connectivity.Connectivity):
    tmpdir = tempfile.TemporaryDirectory()
    dtypes = {}
    
    def save_field(field, optional=False, prefix=''):
        value = getattr(conn, field, None)
        if value is not None:
            if value.dtype == int or value.dtype == bool:
                fmt = '%d'
            else:
                fmt = '%.18e' 
            f = os.path.join(tmpdir.name, f'{prefix}{field}.txt')
            np.savetxt(f, value, fmt=fmt)
        elif not optional:
            raise ValueError(f'Attribute `{field}` not set.')

    for field in ['cortical', 'hemispheres', 'areas', 'tract_lengths']:
        save_field(field, optional=True)
        
    save_field('orientations', optional=True, prefix='average_')
    save_field('weights')
    
    assert conn.region_labels is not None and conn.centres is not None
    with open(os.path.join(tmpdir.name, 'centres.txt'), 'w') as f:
        for label, center in zip(conn.region_labels, conn.centres):
            f.write('%s %.4f %.4f %.4f\n' % (label, *center))
   
    with ZipFile(filename, 'w') as zip_file:
        for fname in os.listdir(tmpdir.name):
            zip_file.write(os.path.join(tmpdir.name, fname), fname)
