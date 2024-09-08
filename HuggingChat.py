from hugchat import hugchat
from hugchat.login import Login
import time

class HugChatManager:
    def __init__(self):
        self.chatbot = None
        self.models = []

    def login(self, email, password):
        try:
            cookie_path_dir = "./cookies/"
            sign = Login(email, password)
            cookies = sign.login(cookie_dir_path=cookie_path_dir, save_cookies=True)
            self.chatbot = hugchat.ChatBot(cookies=cookies.get_dict())
            self.models = self.chatbot.get_available_llm_models()
            self.models = [model.name for model in self.models]
            return True
        except Exception as e:
            print(f"登入失敗: {e}")
            return False

    def chat(self, msg):
        try:
            if self.chatbot is None:
                raise Exception("請先登入 HugChat")
            message_result = self.chatbot.chat(msg)
            message_str: str = message_result.wait_until_done()
            return message_str
        except Exception as e:
            print(f"對話失敗: {e}")
            print("十秒後自動重試...")
            time.sleep(10)
            return self.chat(msg)

    def new_conversation(self, model_index):
        try:
            if self.chatbot is None:
                raise Exception("請先登入 HugChat")
            self.chatbot.new_conversation(model_index, switch_to=True)
        except Exception as e:
            print(f"新增失敗: {e}")
            print("十秒後自動重試...")
            time.sleep(10)
            self.delete_all_conversations()
            self.new_conversation(model_index)

    def delete_all_conversations(self):
        if self.chatbot is None:
            raise Exception("請先登入 HugChat")
        self.chatbot.delete_all_conversations()
