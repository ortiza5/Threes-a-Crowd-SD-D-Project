from app import app
from config import *

if __name__ == "__main__":
	app.secret_key=SECRET
	app.run()