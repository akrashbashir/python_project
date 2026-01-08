# TODO: Connect Project for Testing All Features

## Tasks
- [x] Modify app.py to import data from mewati_model 01.py
- [x] Add Flask routes for morphological features (/morpho/<sentence>)
- [x] Add Flask routes for SpaCy features (/spacy/<sentence>)
- [x] Add Flask routes for Leipzig glossing (/gloss/<sentence>)
- [x] Add Flask routes for X-Bar syntax tree (/tree/<sentence>)
- [x] Add route to list available sentences (/sentences)
- [x] Update home route to provide endpoint information
- [x] Test the Flask app and endpoints
- [x] Verify project is ready for deployment

## Deployment Ready
The project is now ready to be made live. It includes:
- Flask API with endpoints for all Mewati language analysis features
- Procfile for Heroku deployment
- requirements.txt with all dependencies
- runtime.txt specifying Python version
- Can be run locally with `python app.py` or deployed with gunicorn
