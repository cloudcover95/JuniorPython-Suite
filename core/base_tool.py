from PySide6.QtWidgets import QWidget

class BaseTool(QWidget):
    """
    Abstract base class for all PyForge dynamic plugins.
    Enforces structural manifold for UI integration.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app_context = None # Injected at runtime by MainWindow

    @classmethod
    def get_name(cls) -> str:
        raise NotImplementedError("Tool must define a name.")

    def setup_ui(self):
        raise NotImplementedError("Tool must construct its UI tensor here.")
        
    def set_context(self, context):
        self.app_context = context