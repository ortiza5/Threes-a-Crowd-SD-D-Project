from app import app
from config import *

if __name__ == "__main__":
	app.secret_key=SECRET
	app.config['SESSION_TYPE'] = 'filesystem'
	sess.init_app(app)
	app.run()