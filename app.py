from flask import Flask, jsonify, request
import os
import re

# Import data from mewati_model_01.py
from mewati_model_01 import MORPH_FEATURES, SPACY_FEATURES, LEIPZIG_GLOSSING, XBAR_TREES

app = Flask(__name__)

def normalize_sentence(s: str) -> str:
    if not s:
        return ""
    s = s.replace("۔", "").replace("؟", "").replace("!", "").strip()
    s = re.sub(r"\s+", " ", s)
    return s

@app.route('/')
def home():
    return """
    <h1>Mewati Language Model API</h1>
    <p>Available endpoints:</p>
    <ul>
        <li><a href="/hello">/hello</a> - Simple hello endpoint</li>
        <li><a href="/sentences">/sentences</a> - List available sentences</li>
        <li>/morpho/&lt;sentence&gt; - Morphological features</li>
        <li>/spacy/&lt;sentence&gt; - SpaCy features</li>
        <li>/gloss/&lt;sentence&gt; - Leipzig glossing</li>
        <li>/tree/&lt;sentence&gt; - X-Bar syntax tree</li>
    </ul>
    <p>Replace &lt;sentence&gt; with a normalized Mewati sentence (without punctuation).</p>
    """

@app.route('/hello')
def hello():
    return "Hello from Flask!"

@app.route('/sentences')
def get_sentences():
    sentences = list(MORPH_FEATURES.keys())
    return jsonify(sentences)

@app.route('/morpho/<path:sentence>')
def get_morpho(sentence):
    sent = normalize_sentence(sentence)
    if sent not in MORPH_FEATURES:
        return jsonify({"error": f"No morphological features for: {sent}"}), 404
    return jsonify(MORPH_FEATURES[sent])

@app.route('/spacy/<path:sentence>')
def get_spacy(sentence):
    sent = normalize_sentence(sentence)
    if sent not in SPACY_FEATURES:
        return jsonify({"error": f"No SpaCy features for: {sent}"}), 404
    return jsonify(SPACY_FEATURES[sent])

@app.route('/gloss/<path:sentence>')
def get_gloss(sentence):
    sent = normalize_sentence(sentence)
    if sent not in LEIPZIG_GLOSSING:
        return jsonify({"error": f"No Leipzig glossing for: {sent}"}), 404
    return jsonify(LEIPZIG_GLOSSING[sent])

@app.route('/tree/<path:sentence>')
def get_tree(sentence):
    sent = normalize_sentence(sentence)
    tree = XBAR_TREES.get(sent, f"[TP [DP [{sent}]] [T' [T …] [VP …]]]")
    return jsonify({"sentence": sent, "tree": tree})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
