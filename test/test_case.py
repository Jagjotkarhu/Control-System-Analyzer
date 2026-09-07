# tests/test_analyzer.py
import numpy as np  # type: ignore
from src.app4 import TFAnalyzer  # type: ignore
def test_tf_analyzer_initialization():
    """Test if TFAnalyzer correctly initializes a 2nd order system."""
    analyzer = TFAnalyzer([25.0], [1.0, 6.0, 25.0])
    assert analyzer.system_order == 2
    assert analyzer.wn == 5.0
    assert analyzer.zeta == 0.6

def test_time_domain_metrics():
    """Test that time-domain metrics return a valid dictionary with expected keys."""
    analyzer = TFAnalyzer([25.0], [1.0, 6.0, 25.0])
    metrics = analyzer.time_domain_metrics()
    
    assert isinstance(metrics, dict)
    assert 'overshoot' in metrics
    assert 'final_value' in metrics
    assert metrics['overshoot'] > 0.0

def test_freq_domain_metrics():
    """Test that frequency-domain metrics return expected keys and arrays."""
    analyzer = TFAnalyzer([25.0], [1.0, 6.0, 25.0])
    fd_data = analyzer.freq_domain_metrics()
    
    assert isinstance(fd_data, dict)
    assert 'omega' in fd_data
    assert 'mag' in fd_data
    assert 'phase' in fd_data
    assert len(fd_data['omega']) > 0