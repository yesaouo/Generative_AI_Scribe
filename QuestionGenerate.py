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
        Complexity = 5 # default
        # random.sample() returns different elements
        # random.choices() allows same elements
        i = 0
        ls = []
        while i < (Question_num):

            # python 3.9之後的版本被刪了
            #pick_up = random.sample(sentences, k=COMPLEXITY)
            pick_up = self.__select_unique_elements_shuffle(Sentences, Complexity)

            string_sentences = '\n'.join(str(p) for p in pick_up)
            prompt = Template.replace("{usr_msg}", string_sentences)
            response = self.chatbot.chat(prompt)

            # Use regex to find all JSON-like objects
            pattern = r'\{.*?\}'
            response = response.replace('\n', '').replace('\'', '\"')
            response = re.sub(r'\s+', ' ', response).strip()

            # matches is list and separate all {} element
            matches = re.findall(pattern, response)

            # Remove json element which does not contain attribute "question" and "answer"
            try:
                # Ensure matches is a list
                if not isinstance(matches, list):
                    raise TypeError("Expected 'matches' to be a list.")

                # Filter matches to include only those with both "question" and "answer"
                filtered_matches = [m for m in matches if "\"question\"" in m and "\"answer\"" in m]

                # Replace the original list with the filtered one
                matches[:] = filtered_matches
            except TypeError as e:
                print(f"Error: {e}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")

            # Transfer to json object
            try:                
                # Convert the list to a JSON string
                json_string = json.dumps(matches, indent=2)  # 'indent' adds formatting for readability

                ls.extend(json.loads(json_string))
                i += 1
            except Exception:
                print("TF question not conform to JSON.")

        return ls


    def __generate(self, SENTENCES, request):
        sentences = list(set(SENTENCES))

        # True or False questions
        TF_template = \
        """
        <|im_start|>system
        You are a helpful assistant<|im_end|>
        <|im_start|>user
        You are a question generator. Please use the following keyword-sentence pairs to generate some true or false question and provide the answer in JSON format with the attributes are "question" and "answer" respectively, enclosed in curly braces. Respond directly with only the abstract and do not include any additional commentary.
        {usr_msg}<|im_end|>
        <|im_start|>assistant
        """
        TF_q = self.__process(sentences, TF_template, request["TF"])


        # Choosen questions
        CH_template = \
        """
        <|im_start|>system
        You are a helpful assistant<|im_end|>
        <|im_start|>user
        You are a question generator. Please use the following keyword-sentence pairs to generate some multiple-choice question with 4 options and return it in JSON format, enclosed in curly braces. The JSON should include the following attributes: 'question', 'choices', and 'answer'. The 'choices' attribute should be an array containing the four options. Respond directly with only the abstract and do not include any additional commentary.
        {usr_msg}<|im_end|>
        <|im_start|>assistant
        """
        CH_q = self.__process(sentences, CH_template, request["Choose"])


        # Fill blank questions
        BK_template = \
        """
        <|im_start|>system
        You are a helpful assistant<|im_end|>
        <|im_start|>user
        You are a question generator. Please use the following keyword-sentence pairs to generate some fill-in-the-blank question and provide the answer in JSON format with the attributes are "question" and "answer" respectively, enclosed in curly braces. Respond directly with only the abstract and do not include any additional commentary.
        {usr_msg}<|im_end|>
        <|im_start|>assistant
        """
        BK_q = self.__process(sentences, BK_template, request["Blank"])


        # Question Answer questions
        QA_template = \
        """
        <|im_start|>system
        You are a helpful assistant<|im_end|>
        <|im_start|>user
        You are a question generator. Please use the following keyword-sentence pairs to generate some short answer question and provide the answer in JSON format with the attributes are "question" and "answer" respectively, enclosed in curly braces. Respond directly with only the abstract and do not include any additional commentary.
        {usr_msg}<|im_end|>
        <|im_start|>assistant
        """
        QA_q = self.__process(sentences, QA_template, request["QA"])
        
        
        final_structure = {
            "TF": TF_q,  # First sublist
            "CH": CH_q,  # Second sublist
            "BK": BK_q,  # Third sublist
            "QA": QA_q   # Fouth sublist
        }

        # Convert the final structure to a JSON formatted string
        json_output = json.dumps(final_structure, indent=4, ensure_ascii=False)
        json_output = json_output.replace('\\\"', '').replace("\"", '')

        return json_output
    

    def run(self, folder, file_name):

        # 讀取 CSV 文件
        with open(f"resource\\{folder}\\{file_name}\\{file_name}_keyphrase.csv", mode='r', encoding="utf-8") as file:
            reader = csv.reader(file)  # 使用 csv.reader 讀取 CSV 文件
            header = next(reader)  # 讀取並跳過表頭
            data = [tuple(row) for row in reader]  # 將每一行轉換為元組並儲存到列表中

        X = [(r[0], r[2]) for r in data]

        # Default numbers
        req = {
            "TF": 8,
            "Choose": 9,
            "Blank": 6,
            "QA": 4
        }

        return self.__generate(X, req)
    
    def get_json(self, sentences):
        req = {
            "TF": 8,
            "Choose": 9,
            "Blank": 6,
            "QA": 4
        }

        return self.__generate(sentences, req)