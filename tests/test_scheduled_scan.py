import importlib.util
from pathlib import Path
from unittest.mock import MagicMock, patch


def _load_scheduled_scan():
    path = Path(__file__).resolve().parent.parent / "scripts" / "scheduled_scan.py"
    spec = importlib.util.spec_from_file_location("scheduled_scan", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_scheduled_scan_runs(monkeypatch):
    mod = _load_scheduled_scan()
    mock_analyze = MagicMock()
    mock_analyze.invoke = MagicMock(return_value={
        "summary": "Scan 2 pares",
        "results": {"EURUSD": {"found": True}, "XAUUSD": {"found": False}},
    })
    mock_paper = MagicMock(return_value={"alerts": [], "message": "ok"})

    monkeypatch.setattr(mod, "analyze_all_primary_pairs", mock_analyze)
    monkeypatch.setattr(mod, "check_paper_alerts", mock_paper)

    with patch.object(mod, "notify_scan_complete") as mock_scan:
        with patch.object(mod, "notify_setup_found") as mock_setup:
            assert mod.main() == 0
            mock_scan.assert_called_once()
            mock_setup.assert_called_once_with("EURUSD", {"found": True})