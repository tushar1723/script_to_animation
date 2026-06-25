import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from ai_client import generate_scene_breakdown, generate_animation_plan, create_animation_video

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEO_DIR = os.path.join(BASE_DIR, 'videos')
os.makedirs(VIDEO_DIR, exist_ok=True)

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Backend is running'})

@app.route('/api/parse-script', methods=['POST'])
def parse_script():
    data = request.get_json() or {}
    script_text = data.get('script', '').strip()
    if not script_text:
        return jsonify({'error': 'Script text is required'}), 400

    scenes = generate_scene_breakdown(script_text)
    return jsonify({'scenes': scenes})

@app.route('/api/generate-plan', methods=['POST'])
def generate_plan():
    data = request.get_json() or {}
    script_text = data.get('script', '').strip()
    if not script_text:
        return jsonify({'error': 'Script text is required'}), 400

    plan = generate_animation_plan(script_text)
    return jsonify(plan)

@app.route('/videos/<path:filename>', methods=['GET'])
def serve_video(filename):
    return send_from_directory(VIDEO_DIR, filename, as_attachment=False)


@app.route('/api/create-animation', methods=['POST'])
def create_animation():
    data = request.get_json() or {}
    script_text = data.get('script', '').strip()
    selected_options = data.get('options', [])

    if not script_text:
        return jsonify({'error': 'Script text is required'}), 400
    if not isinstance(selected_options, list) or len(selected_options) == 0:
        return jsonify({'error': 'At least one scene must be selected to create animation'}), 400

    animation_response = create_animation_video(script_text, selected_options, video_dir=VIDEO_DIR)
    return jsonify(animation_response)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
