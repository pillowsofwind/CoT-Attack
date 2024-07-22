from run import *
import json
from prompt import *
from utils import *
from math_utils import *
from tqdm import tqdm
import random

client = OpenAI(
    api_key = '',
)

def chatcompletion(messages):
    completion = client.chat.completions.create(
            model='gpt-3.5-turbo-0125',
            messages=messages,
            # max_tokens=4096,
            temperature=1,
            top_p=1
        )
    response = completion.choices[0].message.content.strip()
    return response

tasks = ['GSM', 'HQA', 'CMQA', 'MATHQA', 'STRATEGYQA', 'MATH']
task = tasks[4]

if task in ['GSM', 'HQA', 'MATH']:
    start_time = time.time()
    data_pretest = []
    with open(f'../dataset/{task}.jsonl', 'r') as infile:
        for line in infile:
            data_pretest.append(json.loads(line))

    num = 0
    data_with_wrong_answer = []
    data_without_wrong_answer = []
    for data in tqdm(data_pretest):
        question = data['question']
        gold_answer = data['answer']
        message = [{'role': 'user', 'content': GENERATE_WRONG_ANSWER.format(problem=question)}]
        wrong_answer = chatcompletion(message)
        wrong_answer_1 = clean_response(wrong_answer, task)
        is_correct = check_answer(bot_answer=wrong_answer_1 ,gold_answer=gold_answer,task=task)
        if is_correct == False:
            data['wrong_answer'] = wrong_answer_1
            num += 1
            data_with_wrong_answer.append(data)
        else:
            data['wrong_answer'] = ''
            data_without_wrong_answer.append(data)

    print(f'{task}: {num}')

    with open(f'../dataset/{task}_with_wronng_ans.jsonl', 'w') as outfile:
        for item in data_with_wrong_answer:
            json.dump(item, outfile)
            outfile.write('\n')

    with open(f'../dataset/{task}_without_wronng_ans.jsonl', 'w') as outfile:
        for item in data_without_wrong_answer:
            json.dump(item, outfile)
            outfile.write('\n')
else:
    if task in ['CMQA', 'MATHQA']:
        data_pretest = []
        data_with_wrong_answer = []
        answers = ['a', 'b', 'c', 'd', 'e']
        with open(f'../dataset/{task}.jsonl', 'r') as infile:
            for line in infile:
                data_pretest.append(json.loads(line))
        for data in tqdm(data_pretest):
            question = data['question']
            gold_answer = data['answer'].lower()
            gold_answer_idx = ord(gold_answer) - 97
            for i in range(10):
                idx = random.randint(0,4)
                if idx != gold_answer_idx:
                    random_idx = idx
                    break
            data['wrong_answer'] = answers[random_idx]
            data_with_wrong_answer.append(data)
            
        with open(f'../dataset/{task}_with_wronng_ans.jsonl', 'w') as outfile:
            for item in data_with_wrong_answer:
                json.dump(item, outfile)
                outfile.write('\n')

if task == 'STRATEGYQA':
    data_pretest = []
    data_with_wrong_answer = []
    with open(f'../dataset/{task}.jsonl', 'r') as infile:
        for line in infile:
            data_pretest.append(json.loads(line))
    for data in tqdm(data_pretest):
        question = data['question']
        gold_answer = data['answer']
        if gold_answer == 'True':
            data['wrong_answer'] = 'False'
        else:
            data['wrong_answer'] = 'True'
        data_with_wrong_answer.append(data)
        
    with open(f'../dataset/{task}_with_wronng_ans.jsonl', 'w') as outfile:
        for item in data_with_wrong_answer:
            json.dump(item, outfile)
            outfile.write('\n')