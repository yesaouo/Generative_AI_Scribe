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
        ls = []

        for _ in range(Question_num):
            pick_up = self.__select_unique_elements_shuffle(Sentences, Complexity)
            string_sentences = '\n'.join(str(p) for p in pick_up)
            
            prompt = Template.replace("<Article Content>", string_sentences)
            response = self.chatbot.chat(prompt)

            # 清理並匹配 JSON 字符串
            response = response.replace('\n', '').replace('\'', '\"')
            response = re.sub(r'\s+', ' ', response).strip()
            matches = re.findall(r'\{.*?\}', response)

            # 直接嘗試轉換為 JSON
            for match in matches:
                try:
                    json_obj = json.loads(match)
                    ls.append(json_obj)
                except json.JSONDecodeError:
                    print("Invalid JSON format found, skipping:", match)

        return ls

    def __generate(self, sentences):
        sentences = list(set(sentences))

        # 專屬模板
        TF_template = """
Based on the following article, generate true/false questions in strict JSON format. Do not include any additional text or explanations. Each question should follow this exact structure:  
{ "question": "<true/false question content>", "answer": true/false }.  
Output the questions as a JSON array. Generate at least 5 questions. The article is as follows:  
<Article Content>
        """
        
        CH_template = """
Based on the following article, generate multiple-choice questions with 4 answer options in JSON format. Each question should include:  
- A "question" field with the question text.  
- An "options" field as an array containing 4 answer choices.  
- A "correct_answer" field indicating the correct answer from the options.  

Output the questions as a JSON array. Do not include any text outside the JSON array. Generate at least 5 questions. The article is as follows:  
<Article Content>
        """

        # True or False questions
        TF_q = self.__process(sentences, TF_template, 2)

        valid_TF_q = []
        for item in TF_q:
            question = item.get("question")
            answer = item.get("answer")
            if isinstance(question, str) and isinstance(answer, bool):
                valid_TF_q.append(item)

        TF_q = valid_TF_q

        # Multiple-choice questions
        CH_q = self.__process(sentences, CH_template, 2)

        valid_CH_q = []
        for item in CH_q:
            question = item.get("question")
            options = item.get("options")
            correct_answer = item.get("correct_answer")
            
            if (isinstance(question, str) and
                isinstance(options, list) and
                all(isinstance(opt, str) for opt in options) and
                isinstance(correct_answer, int) and
                1 <= correct_answer <= len(options)):
                valid_CH_q.append(item)

        CH_q = valid_CH_q

        final_structure = {
            "TF": TF_q,
            "CH": CH_q
        }

        return final_structure
    
    def get_quiz(self, sentences):
        return self.__generate(sentences)
