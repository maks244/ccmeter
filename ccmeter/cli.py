"""ccmeter CLI."""

import sys

import fncli

from ccmeter import __version__


@fncli.cli()
def version():
    """print version"""
    print(__version__)


@fncli.cli("ccmeter")
def poll(interval: int = 120, once: bool = False):
    """poll usage API and record samples to local sqlite"""
    from ccmeter.poll import run_poll

    run_poll(interval=interval, once=once)


@fncli.cli("ccmeter")
def report(days: int = 30, json: bool = False):
    """show calibration report: what does 1% actually cost in tokens"""
    from ccmeter.report import run_report

    run_report(days=days, json_output=json)
    if not json:
        from ccmeter.update import check_version

        check_version()


@fncli.cli("ccmeter")
def history(days: int = 7, json: bool = False):
    """show raw usage sample history"""
    from ccmeter.history import show_history

    show_history(days=days, json_output=json)


@fncli.cli("ccmeter")
def status():
    """show current usage and collection stats"""
    from ccmeter.status import show_status

    show_status()
    from ccmeter.update import check_version

    check_version()


@fncli.cli("ccmeter")
def update():
    """check for updates and install latest version"""
    from ccmeter.update import run_update

    run_update()


@fncli.cli("ccmeter")
def export(days: int = 30):
    """dump anonymized calibration data for community sharing"""
    from ccmeter.export import run_export

    run_export(days=days)


@fncli.cli("ccmeter")
def install():
    """install ccmeter as a background daemon (survives restarts)"""
    from ccmeter.daemon import install as do_install

    raise SystemExit(do_install())


@fncli.cli("ccmeter")
def uninstall():
    """stop and remove the background daemon"""
    from ccmeter.daemon import uninstall as do_uninstall

    raise SystemExit(do_uninstall())


def main():
    raise SystemExit(fncli.dispatch(["ccmeter", *sys.argv[1:]]))
