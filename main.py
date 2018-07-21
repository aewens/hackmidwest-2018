#!env/bin/python3

from app import app, manager

if __name__ == "__main__":
    if manager is not None:
        manager.run()

    app.run(debug=True, host="127.0.0.1", port=10101)