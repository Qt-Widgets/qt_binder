from . import qt_api

if qt_api == 'pyqt':
    from PyQt4.QtOpenGL import *  # noqa

else:
    from PySide.QtOpenGL import *  # noqa
