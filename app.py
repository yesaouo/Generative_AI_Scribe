from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import os, shutil, asyncio
from datetime import datetime
from Keyphrase import Keyword
import Resource, Record, LLMChat, GeneticAlgorithm, QuestionGenerate

os.makedirs('uploads', exist_ok=True)
os.makedirs('resource', exist_ok=True)
os.makedirs('records', exist_ok=True)

app = Flask(__name__)
CORS(app)  # 啟用CORS以允許前端跨域請求
FP = Resource.FileProcessor()
RM = Record.RecordManager()
FP.start_processing()
RM.delete_unprocessed_records()
CA = LLMChat.ChatAPI()

@app.route('/api/records', methods=['GET'])
def get_records():
    return jsonify(RM.sort_records())

@app.route('/api/folders', methods=['GET'])
def get_folders():
    FP.start_processing()
    pdf_count = len(FP.get_pdf_files())
    common_count = len(FP.get_finished_files())
    return jsonify({"folders": FP.get_uploads_folders(),"value": common_count, "max": pdf_count})

@app.route('/api/choose', methods=['GET'])
def get_choose():
    pdf_count = len(FP.get_pdf_files())
    common_count = len(FP.get_finished_files())
    return jsonify({"folders": FP.get_resource_folders(),"value": common_count, "max": pdf_count, "models": CA.models})

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
    if len(RM.get_unprocessed_records()) > 0:
        return jsonify({"success": False, "message": f"A conversation is currently active."})
    else:
        process_id = RM.create_record(files)
        keyphrase_path = [os.path.join('resource', f, f'{os.path.basename(f)}_keyphrase.csv') for f in files]
        kw = Keyword()
        kw_result = kw.run(keyphrase_path)
        ga = GeneticAlgorithm.GeneticAlgorithm(process_id, kw_result, CA, model_index)
        ga.start_processing()
        return jsonify({"success": True, "message": f"Execution id {process_id}"})

@app.route('/api/pdf/<string:pdf_path>/<string:pdf_name>')
def serve_pdf(pdf_path, pdf_name):
    pdf_dir = os.path.join('uploads', pdf_path)
    pdf_name += '.pdf'
    return send_from_directory(pdf_dir, pdf_name)

@app.route('/api/record/<string:record_id>', methods=['GET'])
def get_record_content(record_id):
    return render_template('index.html', record=RM.load_record(record_id))

@app.route('/api/record/<string:record_id>/toggle_mark', methods=['POST'])
def toggle_record_mark(record_id):
    return jsonify({"success": RM.toggle_mark(record_id)})

@app.route('/api/record/<string:record_id>/chat', methods=['GET'])
def get_chat_record(record_id):
    chat = RM.load_record(record_id)["chat"]
    DS = LLMChat.DialogueSystem(chat)
    return jsonify(DS.parse_dialogue())

@app.route('/api/record/<string:record_id>/chat', methods=['POST'])
def get_record_chat(record_id):
    message = request.json['message']
    record = RM.load_record(record_id)
    DS = LLMChat.DialogueSystem(record["content"])
    DS.dialogue += record["chat"]
    ask = DS.ask_assistant(message)
    response = CA.chat(ask)
    DS.add_assistant_message(response)
    RM.edit_chat(record_id, DS.get_dialogue_without_system())
    
    return jsonify({'response': response})

@app.route('/api/record/<string:record_id>/quiz', methods=['GET'])
def get_record_quiz(record_id):
    record = RM.load_record(record_id)
    print(record["quiz"])
    return jsonify({'response': record["quiz"]})

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
    FP.start_processing()
    return jsonify({"success": True, "filename": file_name})

@app.route('/api/move', methods=['POST'])
def move_file():
    data = request.json
    folder = data.get('folder')
    new_folder = data.get('new_folder')
    file_name = data.get('file_name')
    return jsonify({"success": FP.move_file(folder, new_folder, file_name)})

@app.route('/api/folder', methods=['DELETE'])
def delete_folder():
    data = request.json
    folder = data.get('folder')
    return jsonify({"success": FP.delete_folder(folder)})

@app.route('/api/delete', methods=['DELETE'])
def delete_file():
    data = request.json
    folder = data.get('folder')
    file_name = data.get('file_name')
    return jsonify({"success": FP.delete_file(folder, file_name)})

if __name__ == '__main__':
    app.run(debug=True)