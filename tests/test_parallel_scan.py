from orb_agent.tools.analyze import analyze_all_primary_pairs


def test_parallel_scan_uses_workers(monkeypatch):
    calls: list[str] = []

    def fake_analysis(pair: str) -> dict:
        calls.append(pair)
        return {"pair": pair, "found": pair == "EURUSD"}

    monkeypatch.setattr("orb_agent.tools.analyze.run_pair_analysis", fake_analysis)
    monkeypatch.setattr("orb_agent.tools.analyze.settings.pairs", "EURUSD,XAUUSD,GBPUSD")
    monkeypatch.setattr("orb_agent.tools.analyze.settings.scan_workers", 3)

    result = analyze_all_primary_pairs.invoke({})
    assert len(calls) == 3
    assert result["found_count"] == 1
    assert result["parallel_workers"] == 3