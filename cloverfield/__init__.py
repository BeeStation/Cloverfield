from cloverfield.app import app, apm
# pylint: skip-file
if __name__ == '__main__':
    # Create a logging handler and attach it.
    handler = LoggingHandler(client=apm.client)
    handler.setLevel(logging.WARN)
    app.logger.addHandler(handler)
