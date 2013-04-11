import sae
import app

application = sae.create_wsgi_app(app.app)
