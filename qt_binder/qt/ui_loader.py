from . import qt_api

if qt_api == 'pyqt':
    def load_ui(path):
        from collections import Counter
        from PyQt4 import uic

        ui = uic.loadUi(path)
        names_hist = Counter()
        for child in ui.children():
            name = child.objectName()
            if name:
                names_hist[name] += 1

        names = []
        for name, count in names_hist.items():
            if count == 1 and not name.startswith('_'):
                names.append(name)

        return ui, names

else:
    def load_ui(path):
        from collections import Counter
        from PySide.QtUiTools import QUiLoader

        class RecordingUiLoader(QUiLoader):
            """ Record the names of widgets as they are created.
            """

            def __init__(self, *args, **kwds):
                self.names = Counter()
                super(RecordingUiLoader, self).__init__(*args, **kwds)

            def to_be_bound(self):
                """ Return the names of child widgets/layouts to be bound.
                """
                names = []
                for name, count in self.names.items():
                    if count == 1 and not name.startswith('_'):
                        names.append(name)
                return names

            def createLayout(self, className, parent=None, name=u''):
                if name:
                    self.names[name] += 1
                layout = super(RecordingUiLoader, self).createLayout(
                    className, parent, name)
                return layout

            def createWidget(self, className, parent=None, name=u''):
                if name:
                    self.names[name] += 1
                widget = super(RecordingUiLoader, self).createWidget(
                    className, parent, name)
                return widget

        loader = RecordingUiLoader()
        ui = loader.load(path)

        return ui, ui.to_be_bound()
