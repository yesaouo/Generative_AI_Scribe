from transformers import AutoModelForTokenClassification, AutoTokenizer, TokenClassificationPipeline
from transformers.pipelines import AggregationStrategy
import torch, os, csv

class Keyword():

    def __init__(self):
        # Load pipeline
        model_name = "ml6team/keyphrase-extraction-kbir-inspec"
        self.extractor = self.KeyphraseExtractionPipeline(model=model_name, device=torch.device('cuda' if torch.cuda.is_available() else 'cpu'))


    class KeyphraseExtractionPipeline(TokenClassificationPipeline):
        '''
        This keyphrase extraction model is very domain-specific and will perform very well on abstracts of scientific papers.
        It's not recommended to use this model for other domains, but you are free to test it out.
        Only works for English documents
        '''
        def __init__(self, model, *args, **kwargs):
            # 初始化模型和tokenizer
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            model_instance = AutoModelForTokenClassification.from_pretrained(model).to(device)  # 移動模型到 GPU
            tokenizer_instance = AutoTokenizer.from_pretrained(model)

            # 呼叫父類別的初始化方法
            super().__init__(
                model=model_instance,
                tokenizer=tokenizer_instance,
                *args,
                **kwargs
            )

        def postprocess(self, all_outputs):
            results = super().postprocess(
                all_outputs=all_outputs,
                aggregation_strategy=AggregationStrategy.SIMPLE,
            )
            # return np.unique([result.get("word").strip() for result in results]) # only words

            # [{'entity_group': 'KEY', 'score': 0.99999523, 'word': ' internet', 'start': 190, 'end': 198},
            # {'entity_group': 'KEY', 'score': 0.9999918, 'word': ' artificial intelligence', 'start': 214, 'end': 237}]
            return results


    def csvIO(self, csv_path, RESULT, action):
        if action == 'r':
            with open(csv_path, 'r', encoding='UTF-8') as file:
                reader = csv.reader(file)
                next(reader)  # 跳過表頭
                return list(reader)
        elif action == 'w':
            with open(csv_path, 'w', encoding='UTF-8', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Keyword', 'Score', 'Sentence'])  # 寫入表頭
                writer.writerows(RESULT)  # 寫入資料
        else:
            raise ValueError("Invalid action. Use 'r' for reading or 'w' for writing.")


    def chunk_extract(self, text):

        def split_text_by_hash_to_extract(text, chunk_size=512):
            chunks = []
            start = 0
            while start < len(text):
                end = start + chunk_size
                if end >= len(text):
                    chunks.append(text[start:])
                    break
                # 找到下一個 '\n' 的位置
                hash_index = text.find('\n', end)
                if hash_index == -1:
                    chunks.append(text[start:])
                    break
                # 將段落加入陣列並更新 start
                chunks.append(text[start:hash_index + 1])
                start = hash_index + 1
            return chunks


        def extract_sentence(text, start_pos, end_pos):
            # Ensure start and end positions are within the text range
            if start_pos < 0 or start_pos > len(text):
                return "Invalid positions"

            # Find the start of the sentence containing the start_pos
            start_sentence_idx = text.rfind('\n', 0, start_pos) + 1
            if start_sentence_idx == 0:  # No period found, start at the beginning
                start_sentence_idx = 0

            # Find the end of the sentence containing the end_pos
            end_sentence_idx = text.find('\n', end_pos)
            if end_sentence_idx == -1:  # No period found, end at the end of the text
                end_sentence_idx = len(text)
            else:
                end_sentence_idx += 1  # Include the period in the extraction

            # Extract and return the sentence
            return text[start_sentence_idx:end_sentence_idx].strip()


        def extract_sentences_with_keywords(text, entities, collection):
            # use end point to find the sentence
            for et in entities:
                collection.append((et['word'].strip(), et['score'], extract_sentence(text, et['start'], et['end'])))

            return collection


        cks = split_text_by_hash_to_extract(text)
        results = []

        for ck in cks:
            r = self.extractor(ck)
            extract_sentences_with_keywords(ck, r, results)

        keyphrase_probs_sents = {}
        for result in results:
            word = result[0] # word
            score = result[1] # score
            ss = result[2] # sentence
            if word not in keyphrase_probs_sents:
                keyphrase_probs_sents[word] = (score, ss)
            else: # Keep the maximum probability if duplicate words are found

                if result[1] > keyphrase_probs_sents[word][0]: # remain larger
                  keyphrase_probs_sents[word] = (score, ss)

                elif result[1] == keyphrase_probs_sents[word][0]: # same score -> combine sentences
                  stcs = keyphrase_probs_sents[word][1].split(' ')
                  stcs += (' ' + ss)
                  # print("STCS IS: " + stcs)
                  keyphrase_probs_sents[word] = (score, stcs)

                else: continue # discard smaller
        #print(f"keyphrase_probs_sents: {keyphrase_probs_sents}\n")

        # Extract unique keyphrases and their probabilities
        keyphrases = list(keyphrase_probs_sents.keys())
        probabilities = [keyphrase_probs_sents[word] for word in keyphrases]
        tuple_list = list(zip(keyphrases, probabilities))
        res = []
        seen_lowercase = set()
        for s, p in tuple_list:
            lower_s = s.lower()
            if lower_s in seen_lowercase: continue

            res.append((s, p[0], p[1]) if ' ' not in s else (lower_s, p[0], p[1]))
            seen_lowercase.add(lower_s)

        res = sorted(res, key = lambda x: x[1], reverse = True)
        return res


    def run(self, file_path, N=100):
        result_list = []

        for csv_path in file_path:
            # If csv was already built
            if os.path.isfile(csv_path): # csv exist
                result_list += self.csvIO(csv_path, None, 'r')
                continue
            # Extract document and build csv
            else:
                # Read document
                with open(csv_path.replace('keyphrase.csv','en.txt'), 'r', encoding='UTF-8') as file:
                    doc = file.read()
                # Extract keywords
                RESULT = self.chunk_extract(doc)
                result_list += RESULT
                # Build csv
                self.csvIO(csv_path, RESULT, 'w')
                
        sorted_data = sorted(result_list, key=lambda x: float(x[1]), reverse=True)
        return sorted_data[:N]