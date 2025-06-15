from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
import subprocess
import json

app = Flask(__name__)
CORS(app)

HISTORY_FILE = 'history.json'

UPLOAD_FOLDER = '../mix'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = file.filename
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    # Assemble the .mixal file
    mix_file = os.path.splitext(filename)[0] + '.mix'
    mix_path = os.path.join(UPLOAD_FOLDER, mix_file)
    asm_result = subprocess.run(['mixasm', filepath], capture_output=True, text=True)

    if asm_result.returncode != 0:
        return jsonify({'error': 'Assembly failed', 'details': asm_result.stderr}), 400

    # Run the compiled .mix file with input to simulate the terminal
    vm_result = subprocess.run(
        ['mixvm', mix_path],
        capture_output=True,
        text=True,
        input='run\nquit\n'
    )

    if vm_result.returncode != 0:
        return jsonify({'error': 'Execution failed', 'details': vm_result.stderr}), 400

    # Extract only the MIX output
    lines = vm_result.stdout.splitlines()
    output_lines = [
        line.strip() for line in lines
        if line.strip() and not any(keyword in line for keyword in [
            "Program loaded", "Start address", "Running", "done",
            "Elapsed time", "Total program time", "Total uptime", "Quitting"
        ])
    ]
    clean_output = "\n".join(output_lines)

        # ✅ Append to history
    timestamp = datetime.now().isoformat()
    new_entry = {
        'timestamp': timestamp,
        'filename': filename,
        'output': clean_output
    }

    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as f:
                history = json.load(f)
        else:
            history = []

        history.append(new_entry)

        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)

    except Exception as e:
        print("Failed to update history:", e)

    return jsonify({'output': clean_output})

@app.route('/history', methods=['GET'])
def get_history():
    with open(HISTORY_FILE, 'r') as f:
        history = json.load(f)
    return jsonify(history)

@app.route('/history/clear', methods=['POST'])
def clear_history():
    with open(HISTORY_FILE, 'w') as f:
        json.dump([], f)
    return jsonify({'message': 'History cleared'})

if __name__ == '__main__':
    app.run(debug=True)
