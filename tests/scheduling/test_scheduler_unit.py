import pytest

from datetime import datetime, timezone

from automation.scheduling import scheduler


@pytest.fixture
def frozen_now():
    # Deterministic UTC timestamp for unit tests (no external libs required)
    return datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


def test_scheduler_signatures_exist(frozen_now):
    assert callable(scheduler.compute_next_run)
    assert callable(scheduler.should_run)


def test_compute_next_run_interval_determinism(frozen_now):
    cfg = {"scheduling": {"mode": "interval", "interval_minutes": 60}}
    n1 = scheduler.compute_next_run(frozen_now, cfg)
    n2 = scheduler.compute_next_run(frozen_now, cfg)
    assert n1 == n2
    assert (n1 - frozen_now).total_seconds() == 3600


def test_compute_next_run_window_today_vs_tomorrow(frozen_now):
    cfg = {"scheduling": {"mode": "window", "window_time": "09:30"}}
    # Now is after window -> next run is tomorrow at 09:30
    nxt_after = scheduler.compute_next_run(frozen_now, cfg)
    assert (nxt_after.date() - frozen_now.date()).days == 1
    assert nxt_after.hour == 9 and nxt_after.minute == 30

    # Now before window -> next run is today at 09:30
    before = datetime(2025, 1, 1, 8, 0, 0, tzinfo=timezone.utc)
    nxt_before = scheduler.compute_next_run(before, cfg)
    assert nxt_before.date() == before.date()
    assert nxt_before.hour == 9 and nxt_before.minute == 30


def test_should_run_interval_and_window(frozen_now):
    # Interval mode: last run an hour earlier -> should run
    cfg_i = {"scheduling": {"mode": "interval", "interval_minutes": 60}}
    last = datetime(2025, 1, 1, 11, 0, 0, tzinfo=timezone.utc)
    assert scheduler.should_run(frozen_now, last, cfg_i)

    # Window mode: before window -> should not run
    cfg_w = {"scheduling": {"mode": "window", "window_time": "13:30"}}
    assert not scheduler.should_run(frozen_now, None, cfg_w)

    # Window mode: after window with no last run -> should run
    cfg_w2 = {"scheduling": {"mode": "window", "window_time": "11:30"}}
    assert scheduler.should_run(frozen_now, None, cfg_w2)

    # Window mode: after window but already ran after window -> should not run
    last_after_window = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    assert not scheduler.should_run(frozen_now, last_after_window, cfg_w2)
