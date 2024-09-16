import csv, random, json, re

class QuestionManager():
    def __init__(self, chatbot):
        self.chatbot = chatbot

    def __select_unique_elements_shuffle(self, lst, k):
        if k > len(lst):
            raise ValueError("k cannot be greater than the length of the list")
        
        shuffled = lst[:]
        random.shuffle(shuffled)
        return shuffled[:k]
    
    def __process(self, Sentences, Template, Question_num):
        Complexity = 5  # 預設複雜度
        i = 0
        ls = []

        while i < Question_num:
            # 隨機挑選句子組合
            pick_up = self.__select_unique_elements_shuffle(Sentences, Complexity)
            string_sentences = '\n'.join(str(p) for p in pick_up)
            
            # 構造聊天機器人輸入的 prompt
            prompt = Template.replace("{usr_msg}", string_sentences)
            response = self.chatbot.chat(prompt)

            # 使用正則表達式匹配所有 JSON-like 的物件
            pattern = r'\{.*?\}'
            response = response.replace('\n', '').replace('\'', '\"')  # 清理不必要的符號
            response = re.sub(r'\s+', ' ', response).strip()  # 確保輸出乾淨

            # 匹配並獲取所有 JSON 物件
            matches = re.findall(pattern, response)

            # 檢查每個物件是否包含 "question" 和 "answer" 屬性
            try:
                # 確保 matches 是一個列表
                if not isinstance(matches, list):
                    raise TypeError("Expected 'matches' to be a list.")

                # 過濾掉不包含 "question" 和 "answer" 的物件
                filtered_matches = [m for m in matches if "\"question\"" in m and "\"answer\"" in m]

                # 如果有合法的 JSON，繼續處理
                if filtered_matches:
                    for match in filtered_matches:
                        # 嘗試將 JSON 字符串轉換為 Python 字典
                        try:
                            json_obj = json.loads(match)
                            ls.append(json_obj)
                        except json.JSONDecodeError:
                            print("Invalid JSON format found, skipping:", match)
                else:
                    print("No valid JSON objects found in response.")

                i += 1  # 遞增計數器以生成下一個問題
            except TypeError as e:
                print(f"Error: {e}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")

        return ls

    def __generate(self, sentences, request):
        sentences = list(set(sentences))

        # 定義一個通用模板函數來處理每種問題模板
        def create_template(template_type, usr_msg="{usr_msg}"):
            return f"""
            <|im_start|>system
            You are a helpful assistant<|im_end|>
            <|im_start|>user
            You are a question generator. Please use the following keyword-sentence pairs to generate some {template_type} and return it in JSON format, enclosed in curly braces. Respond directly with only the abstract and do not include any additional commentary.
            {usr_msg}<|im_end|>
            <|im_start|>assistant
            """

        # True or False questions
        TF_template = create_template("true or false question and provide the answer with the attributes 'question' and 'answer'")
        TF_q = self.__process(sentences, TF_template, request["TF"])

        # Multiple-choice questions
        CH_template = create_template("multiple-choice question with 4 options. The JSON should include 'question', 'choices', and 'answer'")
        CH_q = self.__process(sentences, CH_template, request["Choose"])

        # Fill-in-the-blank questions
        BK_template = create_template("fill-in-the-blank question and provide the answer with the attributes 'question' and 'answer'")
        BK_q = self.__process(sentences, BK_template, request["Blank"])

        # Short answer questions
        QA_template = create_template("short answer question and provide the answer with the attributes 'question' and 'answer'")
        QA_q = self.__process(sentences, QA_template, request["QA"])

        # 最終的 JSON 結構
        final_structure = {
            "TF": TF_q,   # True/False
            "CH": CH_q,   # Multiple-choice
            "BK": BK_q,   # Fill-in-the-blank
            "QA": QA_q    # Short answer
        }

        return final_structure
    
    def get_quiz(self, sentences):
        req = {
            "TF": 3,
            "Choose": 3,
            "Blank": 3,
            "QA": 3
        }

        return self.__generate(sentences, req)