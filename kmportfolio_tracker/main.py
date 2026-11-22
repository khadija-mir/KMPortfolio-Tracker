import logging

from kmportfolio_tracker.cli import run
logger = logging.getLogger(__name__)

def configure_logging():
    logging.basicConfig(
        #log to a file so user screen not overloaded
        filename="app.log",
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        encoding="utf-8",
    )

def main():
    configure_logging()
    logger.info("Portfolio Tracker application started")
    try:
        run()
    # Ctrl+C + Ctrl+Z needs own catch to exit cleanly.
    except (KeyboardInterrupt, EOFError):
        logger.info("Application closed with Ctrl+C or Ctrl+Z (EOF)")
        print("\nGoodbye!")
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