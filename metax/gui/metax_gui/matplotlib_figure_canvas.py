from PySide6.QtWidgets import QWidget, QSizePolicy, QHBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MatplotlibWidget(QWidget):
    def __init__(self, figure=None, parent=None, width=6, height=4, dpi=100):
        """
        A QWidget that embeds a Matplotlib figure with fixed size to prevent deformation.
        
        :param figure: The Matplotlib Figure object. If None, a new Figure is created.
        :param parent: The parent QWidget.
        :param width: Width of the figure in inches.
        :param height: Height of the figure in inches.
        :param dpi: Dots per inch (resolution) of the figure.
        """
        super(MatplotlibWidget, self).__init__(parent)
        
        # Create or use the provided figure
        self.figure = figure if figure else Figure(figsize=(width, height), dpi=dpi)
        self.figure.tight_layout()
        
        # Create the canvas for rendering the figure
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        # Set fixed size for the canvas
        self.canvas.setFixedSize(width * dpi, height * dpi)

        # Create and set layout
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.canvas)
    
    def set_size(self, width, height, dpi=None):
        """
        Update the size of the Matplotlib figure and canvas.
        
        :param width: New width in inches.
        :param height: New height in inches.
        :param dpi: Optional new DPI. If not provided, the current DPI is used.
        """
        dpi = dpi if dpi else self.figure.get_dpi()
        self.figure.set_size_inches(width, height, forward=True)
        self.canvas.setFixedSize(width * dpi, height * dpi)
        self.canvas.draw()
