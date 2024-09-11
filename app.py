from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import os, shutil, asyncio
from datetime import datetime
from Keyphrase import Keyword
import Resource, Record, HuggingChat, GeneticAlgorithm

os.makedirs('uploads', exist_ok=True)
os.makedirs('resource', exist_ok=True)
os.makedirs('records', exist_ok=True)

app = Flask(__name__)
CORS(app)  # 啟用CORS以允許前端跨域請求
RESOURCE = Resource.FileProcessor()
RECORD = Record.RecordManager()
H = HuggingChat.HugChatManager()
RESOURCE.start_processing()
RECORD.delete_unprocessed_records()

@app.route('/api/records', methods=['GET'])
def get_records():
    return jsonify(RECORD.sort_records())

@app.route('/api/folders', methods=['GET'])
def get_folders():
    RESOURCE.start_processing()
    pdf_count = len(RESOURCE.get_pdf_files())
    common_count = len(RESOURCE.get_finished_files())
    return jsonify({"folders": RESOURCE.get_uploads_folders(),"value": common_count, "max": pdf_count})

@app.route('/api/choose', methods=['GET'])
def get_choose():
    pdf_count = len(RESOURCE.get_pdf_files())
    common_count = len(RESOURCE.get_finished_files())
    return jsonify({"folders": RESOURCE.get_resource_folders(),"value": common_count, "max": pdf_count, "models": H.models})

@app.route('/api/terminate', methods=['POST'])
def terminate_app():
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    client_ip = request.remote_addr
    print(f"Termination requested at {current_time} from IP: {client_ip}")
    os._exit(0)

@app.route('/api/process', methods=['POST'])
def process_files():
    data = request.json
    model_index = data.get('model_index')
    files = data.get('files')
    if len(RECORD.get_unprocessed_records()) > 0:
        return jsonify({"success": False, "message": f"A conversation is currently active."})
    else:
        process_id = RECORD.create_record(files)
        keyphrase_path = [os.path.join('resource', f, f'{os.path.basename(f)}_keyphrase.csv') for f in files]
        kw = Keyword()
        kw_result = kw.run(keyphrase_path)
        ga = GeneticAlgorithm.GeneticAlgorithm(process_id, kw_result, H, model_index)
        ga.start_processing()
        return jsonify({"success": True, "message": f"Execution id {process_id}"})

@app.route('/api/pdf/<string:pdf_path>/<string:pdf_name>')
def serve_pdf(pdf_path, pdf_name):
    pdf_dir = os.path.join('uploads', pdf_path)
    pdf_name += '.pdf'
    return send_from_directory(pdf_dir, pdf_name)

@app.route('/api/record/<string:record_id>', methods=['GET'])
def get_record_content(record_id):
    return render_template('index.html', record=RECORD.load_record(record_id))

@app.route('/api/record/<string:record_id>/toggle_mark', methods=['POST'])
def toggle_record_mark(record_id):
    return jsonify({"success": RECORD.toggle_mark(record_id)})

@app.route('/api/record/<string:record_id>/chat', methods=['GET'])
def get_chat_record(record_id):
    chat = RECORD.load_record(record_id)["chat"]
    dialogue_system = HuggingChat.DialogueSystem(chat)
    return jsonify(dialogue_system.parse_dialogue())

@app.route('/api/record/<string:record_id>/chat', methods=['POST'])
def get_record_chat(record_id):
    if len(RECORD.get_unprocessed_records()) > 0:
        return jsonify({'response': '模型正在執行中，請稍後再做嘗試。'})
    
    message = request.json['message']
    record = RECORD.load_record(record_id)
    dialogue_system = HuggingChat.DialogueSystem(record["content"])
    dialogue_system.dialogue += record["chat"]
    ask = dialogue_system.ask_assistant(message)
    response = H.chat(ask)
    dialogue_system.add_assistant_message(response)
    RECORD.edit_chat(record_id, dialogue_system.get_dialogue_without_system())
    
    return jsonify({'response': response})

@app.route('/api/login', methods=['GET'])
def check_login():
    logged_in = H.is_logged_in()
    return jsonify({
        "success": logged_in,
        "message": "已登入" if logged_in else "未登入"
    })

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({
            "success": False,
            "message": "請提供郵箱和密碼"
        }), 400
    
    success = H.login(email, password)
    return jsonify({
        "success": success,
        "message": "登入成功" if success else "登入失敗，請檢查您的郵箱和密碼"
    })

@app.route('/api/upload/<string:folder_name>', methods=['GET'])
def upload_folder(folder_name):
    os.makedirs(os.path.join('uploads', folder_name), exist_ok=True)
    return jsonify({"success": True, "foldername": folder_name})

@app.route('/api/upload/<string:folder_name>', methods=['POST'])
def upload_file(folder_name):
    os.makedirs(os.path.join('uploads', folder_name), exist_ok=True)
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file part"}), 400
    file = request.files['file']
    file_name = file.filename
    if file_name == '':
        return jsonify({"success": False, "error": "No selected file"}), 400
    file.save(os.path.join('uploads', folder_name, file_name))
    RESOURCE.start_processing()
    return jsonify({"success": True, "filename": file_name})

@app.route('/api/move', methods=['POST'])
def move_file():
    data = request.json
    folder = data.get('folder')
    new_folder = data.get('new_folder')
    file_name = data.get('file_name')
    return jsonify({"success": RESOURCE.move_file(folder, new_folder, file_name)})

@app.route('/api/folder', methods=['DELETE'])
def delete_folder():
    data = request.json
    folder = data.get('folder')
    return jsonify({"success": RESOURCE.delete_folder(folder)})

@app.route('/api/delete', methods=['DELETE'])
def delete_file():
    data = request.json
    folder = data.get('folder')
    file_name = data.get('file_name')
    return jsonify({"success": RESOURCE.delete_file(folder, file_name)})

if __name__ == '__main__':
    app.run(debug=True)