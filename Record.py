import json, os, time

class RecordManager:
    def __init__(self, record_folder="records"):
        self.record_folder = record_folder

    def load_records(self):
        records = []
        for filename in os.listdir(self.record_folder):
            if filename.endswith(".json"):
                with open(os.path.join(self.record_folder, filename), 'r', encoding='utf-8') as file:
                    records.append(json.load(file))
        return records

    def sort_records(self):
        records = self.load_records()
        records.sort(key=lambda x: (
            x.get('title') != '' and x.get('content') != '' and x.get('zh_content') != '',  # 未完成的放前面
            not x.get('isMark', False),  # 標記的放第二
            x.get('id')  # 最後按 ID 排序
        ))
        return records

    def get_unprocessed_records(self):
        records = self.load_records()
        return [record for record in records if not record.get('title') or not record.get('content') or not record.get('zh_content')]

    def edit_record(self, id, title=None, content=None, zh_content=None):
        records = self.load_records()
        for record in records:
            if record['id'] == id:
                if title:
                    record['title'] = title
                if content:
                    record['content'] = content
                if zh_content:
                    record['zh_content'] = zh_content
                self.save_record(record)
                return True
        return False

    def toggle_mark(self, id):
        records = self.load_records()
        for record in records:
            if record['id'] == id:
                record['isMark'] = not record['isMark']
                self.save_record(record)
                return True
        return False

    def create_record(self, pdfs):
        id = self.generate_id()
        new_record = {
            "id": id,
            "isMark": False,
            "pdfs": pdfs,
            "title": "",
            "content": "",
            "zh_content": ""
        }
        self.save_record(new_record)
        return id

    def save_record(self, record):
        filename = f"{self.record_folder}/{record['id']}.json"
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(record, file, indent=4)

    def generate_id(self):
        timestamp = int(time.time() * 1000)
        return str(timestamp)

    def delete_unprocessed_records(self):
        unprocessed = self.get_unprocessed_records()
        for record in unprocessed:
            file_path = os.path.join(self.record_folder, f"{record['id']}.json")
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Deleted unprocessed record: {record['id']}")
        
        print(f"Deleted {len(unprocessed)} unprocessed records.")
        return len(unprocessed)
