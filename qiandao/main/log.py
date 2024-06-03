#!/usr/bin/env python

def configure_logging(debug: bool, base_dir):
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "rich": {
                "format": "%(message)s"
            },
            "file": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        },
        "handlers": {
            "console": {
                "formatter": "rich",
                "class": "rich.logging.RichHandler",
                "show_path": False,
                "omit_repeated_times": False,
                "log_time_format": "%Y/%m/%d %X",
            },
            "file": {
                "formatter": "file",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": base_dir / "storages/logs/qiandao.log"
            },
            "django.file": {
                "formatter": "file",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": base_dir / "storages/logs/django.log"
            }
        },
        "loggers": {
            "qiandao": {
                "level": "DEBUG" if debug else "INFO",
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "django.server": {
                "level": "DEBUG" if debug else "INFO",
                "handlers": ["console", "django.file"],
                "propagate": False,
            }
        }
    }
