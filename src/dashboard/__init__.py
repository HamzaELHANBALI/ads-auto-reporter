"""Interactive dashboard and visualization components."""

# Legacy Dash visualizer - only import if needed
# from .visualizer import DashboardVisualizer

# PDF export - optional, only import if reportlab is available
try:
    from .export import PDFExporter
    __all__ = ["PDFExporter"]
except ImportError:
    # reportlab not installed, PDF export unavailable
    __all__ = []




