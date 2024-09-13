import requests, json, re

class ChatAPI:
    def __init__(self, host=None):
        self.host = host if host is not None else "http://localhost:11434"
        self.models = self.fetch_models()  # 從 API 獲取模型名稱

    def fetch_models(self):
        # 從指定的 host 獲取模型數據
        api_url = f"{self.host}/api/tags"
        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                data = response.json()
                # 提取所有模型的名稱
                model_names = [model["name"] for model in data.get("models", [])]
                return model_names if model_names else ["default_model"]
            else:
                print(f"Error fetching models: {response.status_code}")
                return ["default_model"]
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return ["default_model"]

    def chat(self, prompt, model_index=0, num_ctx=2048):
        # 構建要發送的數據
        api_url = f"{self.host}/api/generate"  # 根據 host 構建完整的 API 路徑
        data = {
            "model": self.models[model_index],
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_ctx": num_ctx
            }
        }

        # 發送 POST 請求
        try:
            response = requests.post(api_url, data=json.dumps(data), headers={"Content-Type": "application/json"})
            if response.status_code == 200:
                return response.json().get("response", "No response found")
            else:
                print(f"Error: {response.status_code}, {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")


class DialogueSystem:
    def __init__(self, system_message):
        self.dialogue = f"<|im_start|>system\n{system_message}\n<|im_end|>\n"
        self.system_message = f"<|im_start|>system\n{system_message}\n<|im_end|>\n"

    def add_user_message(self, message):
        self.dialogue += f"<|im_start|>user\n{message}\n<|im_end|>\n"

    def add_assistant_message(self, message):
        self.dialogue += f"<|im_start|>assistant\n{message}\n<|im_end|>\n"
    
    def ask_assistant(self, message):
        self.add_user_message(message)
        return self.dialogue + "<|im_start|>assistant\n"

    def get_dialogue(self):
        return self.dialogue

    def get_dialogue_without_system(self):
        return self.dialogue.replace(self.system_message, "")
    
    def parse_dialogue(self):
        # 正則表達式拆分對話
        pattern = r"<\|im_start\|>(user|assistant|system)\n(.*?)\n<\|im_end\|>"
        matches = re.findall(pattern, self.dialogue, re.DOTALL)
        
        parsed_dialogue = []
        for match in matches:
            role, message = match
            parsed_dialogue.append({
                'role': role,
                'message': message.strip()
            })
        
        return parsed_dialogue
