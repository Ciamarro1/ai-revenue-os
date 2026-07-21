import pytest
import time
from unittest.mock import MagicMock

from src.revenue_os.tracking.timing_context import TimingContext


def test_timing_measures_elapsed():
    with TimingContext("test_op") as tc:
        time.sleep(0.1)
    assert tc.elapsed >= 0.09
    assert tc.elapsed < 1.0


def test_timing_logs_to_mlflow():
    mock_tracker = MagicMock()
    with TimingContext("test_op", mlflow_tracker=mock_tracker) as tc:
        time.sleep(0.05)
    mock_tracker.log_metrics.assert_called_once()
    args = mock_tracker.log_metrics.call_args[0][0]
    assert "timing_test_op_seconds" in args
    assert args["timing_test_op_seconds"] >= 0.04


def test_timing_without_tracker():
    with TimingContext("test_op") as tc:
        pass
    assert tc.elapsed >= 0.0


def test_timing_exception_passthrough():
    with pytest.raises(ValueError, match="test error"):
        with TimingContext("test_op") as tc:
            raise ValueError("test error")
    assert tc.elapsed >= 0.0


def test_timing_context_as_variable():
    with TimingContext("test_op") as tc:
        time.sleep(0.05)
    # After exit, elapsed should be accessible
    assert isinstance(tc.elapsed, float)
    assert tc.name == "test_op"
