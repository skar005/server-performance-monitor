from alerting import check_threshold


def test_cpu_below_threshold():
    result = check_threshold("cpu", 50)

    assert result is None


def test_cpu_above_threshold():
    result = check_threshold("cpu", 90)

    assert result is not None
    assert result["metric"] == "cpu"
    assert result["value"] == 90


def test_memory_below_threshold():
    result = check_threshold("memory", 50)

    assert result is None


def test_disk_above_threshold():
    result = check_threshold("disk", 95)

    assert result is not None
    assert result["metric"] == "disk"
