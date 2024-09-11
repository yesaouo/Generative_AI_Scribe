from dotenv import load_dotenv, set_key
from hugchat import hugchat
from hugchat.login import Login
import os, time, re

class HugChatManager:
    def __init__(self):
        self.chatbot = None
        self.models = []
        self.email = None
        self.password = None
        self.load_credentials()
        if self.email and self.password:
            self.login(self.email, self.password)

    def load_credentials(self):
        load_dotenv()
        self.email = os.getenv('HUGCHAT_EMAIL')
        self.password = os.getenv('HUGCHAT_PASSWORD')

    def save_credentials(self):
        if self.email and self.password:
            set_key('.env', 'HUGCHAT_EMAIL', self.email)
            set_key('.env', 'HUGCHAT_PASSWORD', self.password)

    def login(self, email, password):
        try:
            cookie_path_dir = "./cookies/"
            sign = Login(email, password)
            cookies = sign.login(cookie_dir_path=cookie_path_dir, save_cookies=True)
            self.chatbot = hugchat.ChatBot(cookies=cookies.get_dict())
            self.models = self.chatbot.get_available_llm_models()
            self.models = [model.name for model in self.models]
            self.email = email
            self.password = password
            self.save_credentials()
            return True
        except Exception as e:
            print(f"登入失敗: {e}")
            self.chatbot = None
            self.models = []
            return False

    def is_logged_in(self):
        return self.chatbot is not None

    def get_login_status(self):
        if self.is_logged_in():
            return f"已登入 (Email: {self.email})"
        else:
            return "未登入"

    def chat(self, msg, model_index=0, max_retries=3):
        if not self.is_logged_in():
            print("請先登入 HugChat")
            return "錯誤：chatbot 未初始化，請先登入。"

        retries = 0
        while retries < max_retries:
            try:
                self.chatbot.new_conversation(model_index, switch_to=True)
                message_result = self.chatbot.chat(msg)
                message_str: str = message_result.wait_until_done()
                return message_str
            except Exception as e:
                print(f"對話失敗: {e}")
                print("嘗試刪除所有對話...")
                
                try:
                    self.chatbot.delete_all_conversations()
                except Exception as delete_exception:
                    print(f"刪除對話失敗: {delete_exception}")
                
                retries += 1
                if retries < max_retries:
                    wait_time = 10 * retries
                    print(f"{wait_time}秒後自動重試...")
                    time.sleep(wait_time)
                else:
                    print("已達到最大重試次數，無法完成對話。")
                    return "錯誤：無法完成對話，請稍後再試。"

        return "錯誤：對話失敗，請檢查網絡連接或稍後再試。"

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
