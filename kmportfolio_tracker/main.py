import logging

from kmportfolio_tracker.cli import run


def main():
    logging.basicConfig(
        filename="app.log",
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        encoding="utf-8",
    )

    logger = logging.getLogger(__name__)
    logger.info("Portfolio Tracker application started")

    try:
        run()
    except Exception:
        logger.exception("An unexpected error occurred")
        print(
            "\nAn unexpected error occurred. "
            "Please check app.log for details."
        )
    finally:
        logger.info("Portfolio Tracker application stopped")


if __name__ == "__main__":
    main()