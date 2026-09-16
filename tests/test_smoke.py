"""Smoke tests to verify project packaging and environment setup."""

import habits


def test_package_version() -> None:
    """Verify that habits package exposes the expected version string."""
    assert hasattr(habits, "__version__")
    assert habits.__version__ == "0.1.0"


def test_main_module_importable() -> None:
    """Verify that habits.__main__ module can be imported cleanly."""
    import habits.__main__

    assert habits.__main__ is not None
