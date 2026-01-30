import base64
import json
from pathlib import Path

from flask import Blueprint, current_app, jsonify, send_from_directory

encoded_js_bp = Blueprint("encoded_js", __name__)


@encoded_js_bp.route("/js/<path:filename>")
def get_encoded_js(filename):
    js_encoded_dir = Path(current_app.root_path) / "static" / "js_encoded"
    json_file = js_encoded_dir / f"{filename}.json"

    if json_file.exists():
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data)

    js_file = Path(current_app.root_path) / "static" / "js" / filename

    if not js_file.exists():
        return jsonify({"error": "File not found"}), 404

    with open(js_file, "rb") as f:
        js_content = f.read()

    encoded_content = base64.b64encode(js_content).decode("utf-8")

    data = {
        "original_file": str(js_file),
        "encoded_content": encoded_content,
        "size": len(js_content),
        "encoded_size": len(encoded_content),
    }

    return jsonify(data)


@encoded_js_bp.route("/js/raw/<path:filename>")
def get_raw_js(filename):
    return send_from_directory("static/js", filename)


def load_js_files(*filenames):
    from flask import Markup, url_for

    loader_url = url_for("static", filename="js/js-loader.js")
    loader_script = f"""
    <script src="{loader_url}"></script>
    <script>
    document.addEventListener('DOMContentLoaded', function() {{
        const scriptsToLoad = {json.dumps(list(filenames))};
        jsLoader.loadMultiple(scriptsToLoad);
    }});
    </script>
    """

    return Markup(loader_script)


def register_template_helpers(app):
    app.jinja_env.globals.update(load_js_files=load_js_files)
