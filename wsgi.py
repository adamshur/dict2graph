"""WSGI entry point for production deployment."""

from dictionary_graph.web.app import app

if __name__ == '__main__':
    app.run()