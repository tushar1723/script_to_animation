import json
import os
import requests
import time
import uuid
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
GOOGLE_AI_STUDIO_API_KEY = os.environ.get('GOOGLE_AI_STUDIO_API_KEY')

try:
    import openai
except ImportError:
    openai = None


def _openai_available():
    return openai is not None and OPENAI_API_KEY


def _safe_parse_json(text):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def generate_scene_breakdown(script_text: str):
    if _openai_available():
        openai.api_key = OPENAI_API_KEY
        prompt = (
            "You are an AI scene planner. Convert the user script into a JSON array of scenes. "
            "Each scene must include sceneNumber, description, characters, setting, mood, and action. "
            "Return only valid JSON.\n\n"
            f"Script:\n{script_text}\n"
        )
        response = openai.ChatCompletion.create(
            model='gpt-4o-mini',
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.8,
            max_tokens=600,
        )
        content = response.choices[0].message.content.strip()
        parsed = _safe_parse_json(content)
        if parsed:
            return parsed

    # Fallback stub
    return [
        {
            'sceneNumber': 1,
            'description': 'Opening scene that introduces the main character and setting.',
            'characters': ['Hero'],
            'setting': 'City street at dusk',
            'mood': 'hopeful and adventurous',
            'action': 'The hero walks toward an old theater while music swells.',
        },
        {
            'sceneNumber': 2,
            'description': 'A dramatic turn where the hero discovers a hidden clue.',
            'characters': ['Hero', 'Guide'],
            'setting': 'Secret alley behind the theater',
            'mood': 'mysterious and tense',
            'action': 'The hero reads a glowing note and decides to follow it.',
        },
    ]


def generate_animation_plan(script_text: str):
    if _openai_available():
        openai.api_key = OPENAI_API_KEY
        prompt = (
            "You are an animation production planner. Given the script, return a JSON object with sceneAssets and audioAssets arrays. "
            "Each scene asset should include sceneNumber, imagePrompt, animationNotes, and transition. "
            "Each audio asset should include sceneNumber, dialogue, voiceStyle, and soundEffects. "
            f"Script:\n{script_text}\n"
        )
        response = openai.ChatCompletion.create(
            model='gpt-4o-mini',
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.8,
            max_tokens=700,
        )
        content = response.choices[0].message.content.strip()
        parsed = _safe_parse_json(content)
        if parsed:
            return parsed

    # Fallback stub
    return {
        'sceneAssets': [
            {
                'sceneNumber': 1,
                'imagePrompt': 'An adventurous hero walking down a neon-lit city street at dusk',
                'animationNotes': 'Slow camera dolly in, character walk cycle, soft glowing street lights.',
                'transition': 'fade toward scene 2 with a shimmering overlay',
            },
            {
                'sceneNumber': 2,
                'imagePrompt': 'A mysterious hidden alley behind a theater with glowing symbols',
                'animationNotes': 'Quick cut to reveal the clue, dramatic shadows, close-up on note.',
                'transition': 'cut to black and then reveal next scene with suspense music',
            },
        ],
        'audioAssets': [
            {
                'sceneNumber': 1,
                'dialogue': 'This city holds more secrets than I ever imagined.',
                'voiceStyle': 'clear, curious, and determined',
                'soundEffects': ['city ambience', 'footsteps', 'distant horns'],
            },
            {
                'sceneNumber': 2,
                'dialogue': 'A clue? I need to find out where this leads.',
                'voiceStyle': 'quiet, urgent, and focused',
                'soundEffects': ['whispering wind', 'muffled footsteps', 'paper rustle'],
            },
        ],
    }


def _download_remote_video(video_url: str, video_dir: str):
    try:
        response = requests.get(video_url, stream=True, timeout=120)
        response.raise_for_status()

        extension = 'mp4'
        filename = f"animation_{int(time.time())}_{uuid.uuid4().hex}.{extension}"
        filepath = os.path.join(video_dir, filename)

        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return filename
    except Exception:
        return None


def _create_google_video(prompt: str, video_dir: str):
    if not GOOGLE_AI_STUDIO_API_KEY:
        return None

    url = (
        'https://generativestudio.googleapis.com/v1beta1/models/video-bison-1:generate'
        f'?key={GOOGLE_AI_STUDIO_API_KEY}'
    )
    payload = {
        'prompt': prompt,
        'resolution': '1080p',
        'format': 'mp4',
        'audio': True,
    }

    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        video_url = (
            data.get('output', {}).get('uri')
            or data.get('artifactUri')
            or (data.get('artifacts') or [{}])[0].get('uri')
        )

        if not video_url:
            return {'rawResponse': data}

        saved_filename = _download_remote_video(video_url, video_dir)
        if saved_filename:
            return {
                'videoUrl': f'/videos/{saved_filename}',
                'savedFileName': saved_filename,
                'rawResponse': data,
            }

        return {'videoUrl': video_url, 'rawResponse': data}
    except Exception:
        return None


def create_animation_video(script_text: str, selected_options: list, video_dir: str):
    prompt_items = []
    for option in selected_options:
        prompt_items.append(
            f"Scene {option.get('sceneNumber')}: {option.get('imagePrompt')} | "
            f"Style: {option.get('animationStyle')} | Transition: {option.get('transition')}"
        )
    prompt = (
        'Create a short animated video using the selected scenes and styles. '
        'Use the following scene instructions:\n' + '\n'.join(prompt_items)
    )

    google_result = _create_google_video(prompt, video_dir)
    if google_result and google_result.get('videoUrl'):
        return {
            'title': 'AI Studio Generated Animation',
            'description': 'Video generated using Google AI Studio based on your selected scene options.',
            'videoUrl': google_result['videoUrl'],
            'selectedScenes': selected_options,
            'rawResponse': google_result.get('rawResponse'),
        }

    if _openai_available():
        openai.api_key = OPENAI_API_KEY
        prompt = (
            "You are an animation assistant. The user selected specific scene animations from the plan. "
            "Return a JSON object containing a videoUrl, title, description, and selectedScenes. "
            "Each selected scene should include sceneNumber, animationStyle, transition, and imagePrompt. "
            f"Script:\n{script_text}\n"
            f"Selections:\n{json.dumps(selected_options, indent=2)}\n"
        )
        response = openai.ChatCompletion.create(
            model='gpt-4o-mini',
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.7,
            max_tokens=500,
        )
        content = response.choices[0].message.content.strip()
        parsed = _safe_parse_json(content)
        if parsed:
            return parsed

    return {
        'title': 'Generated animation preview',
        'description': 'A placeholder animation video has been created from your selected scenes and styles. Replace this with a real video export integration later.',
        'videoUrl': 'https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4',
        'selectedScenes': selected_options,
    }
