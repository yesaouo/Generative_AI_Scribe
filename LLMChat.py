import requests, json, re

class ChatAPI:
    def __init__(self, host=None):
        self.host = host if host is not None else "http://localhost:11434"
        self.models = []

    def check_backend(self, ignore_check=False):
        if ignore_check:
            print("警告：忽略 Ollama 後端檢查。")
            print("請注意：")
            print("1. 某些依賴於 Ollama 後端的功能可能無法正常工作。")
            print("2. 如果遇到與模型或 API 相關的錯誤，請確保 Ollama 後端已正確配置並運行。")
            print("3. 在生產環境中，建議啟用後端檢查以確保系統穩定性。")
            return True

        self.models = self.fetch_models()
        if not self.models:
            print("警告：沒有可用的模型。請確保已安裝模型或 Ollama 後端已啟動。")
            print("如果要忽略此檢查，請使用 --ignore-backend-check 參數。")
            return False
        return True

    def fetch_models(self):
        api_url = f"{self.host}/api/tags"
        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                data = response.json()
                model_names = [model["name"] for model in data.get("models", [])]
                return model_names if model_names else []
            else:
                print(f"Error fetching models: {response.status_code}")
                return []
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return []

    def chat(self, prompt, model_index=0, num_ctx=2048):
        if len(self.models) < 1:
            return
        
        api_url = f"{self.host}/api/generate"
        data = {
            "model": self.models[model_index],
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_ctx": num_ctx
            }
        }

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
