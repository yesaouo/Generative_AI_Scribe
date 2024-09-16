import random, math, time, threading
import numpy as np
from adaptive_semantic_similarity import AggregateEmbeddings
from QuestionGenerate import QuestionManager
from Record import RecordManager

class GeneticAlgorithm:
    def __init__(self, process_id, keyphrase_result, chatbot, model_index=0, mutation_rate=0.1, population_size=None, generations=None, N=None,):
        self.chatbot = chatbot
        self.model_index = model_index
        self.process_id = process_id
        self.keyphrase_result = keyphrase_result
        self.mutation_rate = mutation_rate
        self.population_size = population_size if population_size else len(keyphrase_result) // 4
        self.generations = generations if generations else len(keyphrase_result) // 5
        self.N = N if N else len(keyphrase_result) // 8
        self.keywords = [r[0] for r in keyphrase_result]
        self.probability = [float(r[1]) for r in keyphrase_result]
        self.sentences = [r[2] for r in keyphrase_result]
        self.article = ' '.join(list(set(self.sentences)))

        # 印出基因演算法的參數
        print("=" * 50)
        print(f"Genetic Algorithm Initialized with the following parameters:")
        print(f"Process ID: {self.process_id}")
        print(f"Population Size: {self.population_size}")
        print(f"Generations: {self.generations}")
        print(f"Mutation Rate: {self.mutation_rate}")
        print(f"Number of Sentences: {self.N}")
        print("=" * 50)

    def __get_summarize(self, sentences):
        TEMPLATE = """
        <|im_start|>system
        You are a helpful assistant<|im_end|>
        <|im_start|>user
        You are an article generator. Please generate an original abstract based on the following sentences. Ensure that the abstract is direct, clear, and confident. Respond directly with only the abstract and do not include any additional commentary.
        {usr_msg}<|im_end|>
        <|im_start|>assistant
        """
        sentences = '\n'.join(sentences)
        prompt = TEMPLATE.replace("{usr_msg}", sentences)
        return self.chatbot.chat(prompt, self.model_index)
    
    def __get_zh_summarize(self, summarize):
        prompt = f"將底下的文章翻譯，不要做額外的回覆\n\n{summarize}"
        return self.chatbot.chat(prompt, self.model_index)
    
    def __get_summarize_title(self, summarize):
        prompt = f"Give the article below a title without any additional replies.\n\n{summarize}"
        return self.chatbot.chat(prompt, self.model_index)

    def __generate_random_sentence(self, sentences, probability):
        total = sum(probability)
        normalized_probabilities = [p / total for p in probability]
        cumulative_prob = np.cumsum(normalized_probabilities)
        selected_item = []

        for i in range(self.N):
            r = np.random.rand()
            idx = np.where(cumulative_prob >= r)[0][0]
            selected_item.append(sentences[idx])

        return tuple(selected_item)

    def __fitness(self, sentence, doc):
        calculator = AggregateEmbeddings()
        score = calculator.get_similarity(sentence, doc)
        return score

    def __crossover(self, parent1, parent2):
        crossover_point = random.randint(1, len(parent1) - 1)
        child1 = parent1[:crossover_point] + parent2[crossover_point:]
        child2 = parent2[:crossover_point] + parent1[crossover_point:]
        return child1, child2

    def __mutate(self, keywords, document_keywords):
        if random.random() < self.mutation_rate:
            new_keyword = random.choice(document_keywords)
            index_to_replace = random.randint(0, self.N - 1)
            new_keywords = list(keywords)
            new_keywords[index_to_replace] = new_keyword
            new_keywords = tuple(new_keywords)
            return new_keywords
        else:
            return keywords

    def run(self):
        start_time = time.time()  # 開始時間
        population = [self.__generate_random_sentence(self.sentences, self.probability) for _ in range(self.population_size)]
        keyword_pair_similarity = {}
        best_response = ""
        generation_max_score = 0.0

        for generation in range(self.generations):
            fitness_scores = []
            for index, sentence in enumerate(population):
                sorted_sentence = tuple(sorted(sentence))
                if sorted_sentence not in keyword_pair_similarity:
                    llm_response = self.__get_summarize(sentence)
                    score = self.__fitness(self.article, llm_response)

                    if score > generation_max_score:
                        generation_max_score = score
                        best_response = llm_response

                    fitness_scores.append(score)
                    keyword_pair_similarity[sorted_sentence] = score
                else:
                    fitness_scores.append(keyword_pair_similarity[sorted_sentence])

            combined = list(zip(population, fitness_scores))
            sorted_combined = sorted(combined, key=lambda x: x[1], reverse=True)

            new_population = []
            s = int((10 * self.population_size) / 100)
            new_population.extend(pair[0] for pair in sorted_combined[:s])

            s = self.population_size - len(new_population)

            for _ in range(s):
                k = math.ceil(0.8 * self.population_size)
                selected_elements = random.sample(sorted_combined[:k], 2)
                parent1, parent2 = [pair[0] for pair in selected_elements]

                offspring1, offspring2 = self.__crossover(parent1, parent2)
                new_population.append(self.__mutate(offspring1, self.sentences))
                new_population.append(self.__mutate(offspring2, self.sentences))

            population = new_population[:self.population_size]

            TEMP_RESPONSE = best_response.replace('\n', '')
            print(f"Generation {generation + 1}/{self.generations} completed.")
            print(f'Fitness: {max(fitness_scores)}')
            print(f'Best Sentence: {population[fitness_scores.index(max(fitness_scores))]}')
            print(f'Best Response: {TEMP_RESPONSE}\n')

        final_fitness_index = max(range(len(fitness_scores)), key=lambda i: fitness_scores[i])
        final_sentence = population[final_fitness_index]

        print(f'Final Fitness: {fitness_scores[final_fitness_index]}')
        print(f'Final Best Sentence: {final_sentence}')
        print(f'Final Best Response: {best_response}\n')

        title = self.__get_summarize_title(best_response)
        content = best_response
        zh_content = self.__get_zh_summarize(best_response)
        
        QM = QuestionManager(self.chatbot)
        quiz = QM.get_quiz(self.sentences)

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Total Execution Time: {elapsed_time:.2f} seconds.")

        RM = RecordManager()
        RM.edit_record(self.process_id, title, content, zh_content, quiz, elapsed_time)
    
    def start_processing(self):
        thread = threading.Thread(target=self.run)
        thread.daemon = True
        thread.start()
