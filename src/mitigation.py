from utils import *
from prompt import *
import json
import re
import numpy as np
from tqdm.auto import tqdm
import time
from math_utils import *

ANS_RE = re.compile(r"#### (\-?[0-9\.\,]+)")
INVALID_ANS = "[invalid]"
NUM_SC=10

def chat(messages, temperature=0, top_p=0):
    completion = chat_completion_with_backoff(
        model='gpt-3.5-turbo-0125',
        messages=messages,
        # max_tokens=4096,
        temperature=temperature,
        top_p=top_p
    )
    # print("OK")
    response = completion.choices[0].message.content.strip()
    return response


def check_answer(bot_answer,gold_answer,task):
    if task == 'GSM':
        gt_answer = extract_answer(gold_answer,task=task).lower()
        assert gt_answer != INVALID_ANS
        if isinstance(bot_answer, list):
            return gt_answer in bot_answer
        else:
            return gt_answer == str(bot_answer)
    elif task == 'HQA':
        # print(f'Gold answer: {gold_answer}')
        # print(f'Bot answer: {bot_answer}')
        gt_answer = extract_answer(gold_answer,task=task).lower()
        assert gt_answer != INVALID_ANS
        return gt_answer in bot_answer
    elif task == 'CMQA':
        gt_answer = extract_answer(gold_answer,task=task).lower()
        assert gt_answer != INVALID_ANS
        return gt_answer == bot_answer
    elif task == 'MATHQA':
        gt_answer = extract_answer(gold_answer,task=task).lower()
        assert gt_answer != INVALID_ANS
        return gt_answer == bot_answer
    elif task == 'STRATEGYQA':
        gt_answer = extract_answer(gold_answer,task=task).lower()
        assert gt_answer != INVALID_ANS
        return gt_answer == bot_answer
    elif task == 'MATH':
        gt_answer = extract_answer(gold_answer,task=task).lower()
        assert gt_answer != INVALID_ANS
        return is_equiv(gt_answer, bot_answer)
    else:
        raise NotImplementedError(f"Required task for check answer: {task} is NOT implemented!")
    

# default extractor
def extract_answer(completion, task):
    if task == 'GSM':
        match = ANS_RE.search(completion)
        if match:
            match_str = match.group(1).strip()
            match_str = match_str.replace(",", "")
            return match_str
        else:
            return INVALID_ANS
    elif task == 'HQA':
        if completion is not None:
            return completion
        else:
            return INVALID_ANS
    elif task == 'CMQA':
        if completion is not None:
            return completion.strip()
        else:
            return INVALID_ANS
    elif task == 'MATHQA':
        if completion is not None:
            return completion.strip()
        else:
            return INVALID_ANS
    elif task == 'STRATEGYQA':
        if completion is not None:
            if completion == 'True':
                return 'yes'
            else:
                return 'no'
        else:
            return INVALID_ANS
    elif task == 'MATH':
        if completion is not None:
            return completion.strip()
        else:
            return INVALID_ANS

# extract answer after [Answer]
def clean_response(response,task):
    split_response = response.lower().split('[answer]')
    if len(split_response) > 1:
        response = split_response[1] # only for the first answer
        if task == 'HQA':
            return response
        if task == 'CMQA':
            return response[1:2]
        if task == 'MATHQA':
            return response[1:2]
        if task == 'MATH':
            return extract(response)
        if task == 'STRATEGYQA':
            if 'yes' in response:
                return 'yes'
            elif 'no' in response:
                return 'no' 
            else:
                return ''
        if task == 'GSM':
            regrex = re.compile(r"(-?\d+(?:[.,/]\d+)*)(?!\d)")
            # try_text = "The values are -1,234.56, 123/456, and .78 but not ,123 or 456. not therefore, and ..."
            # matches = regrex.search(response)
            # if matches:
            #     # print(matches)
            #     bot_ans = matches.group(1).strip().replace(",","")
            #     bot_ans = re.sub(r'\.$', '', bot_ans)
            #     return bot_ans
            matches = regrex.findall(response)
            if matches:
                # multiple ans
                bot_ans = [match.strip().replace(",", "").rstrip('.') for match in matches]
                return bot_ans
            else:
                return response.strip()
    else:
        return ""


# only used for attack methods, figure out final answer
def get_final_answer(response,task,problem,attack):
    # print(f'Original: {response}')
    response = response.lower()
    if attack == 1:
        start_index = response.find("[answer]")
        if start_index != -1:
            end_index = response.find("\n", start_index)
            if end_index != -1:
                response = response[:start_index] + response[end_index + 1:]
    # print(f'Processed: {response}')
    if task == 'CMQA' or task == 'MATHQA':
        messages = [{"role":"user","content":FIND_FINAL_ANSWER_CHOICES.format(problem=problem,rationale=response)}]
    elif task == 'STRATEGYQA':
        messages = [{"role":"user","content":FIND_FINAL_ANSWER_JUDGE.format(problem=problem,rationale=response)}]
    else:
        messages = [{"role":"user","content":FIND_FINAL_ANSWER.format(problem=problem,rationale=response)}]
    res=chat(messages=messages)
    #print(f'Extracted: {res}')
    return clean_response(res,task)



def get_answer(problem,method,task,attack=0,wrong_answer="", mit_method=None):
    messages=[]
    messages.append({"role":"system","content":SYS})
    if method == 'ZS':
        messages.append({"role":"user","content":ZS.format(problem=problem)})
    elif method == 'ZS_CoT':
        messages.append({"role":"user","content":ZS_CoT.format(problem=problem)})
    elif method == 'FS_CoT':
        if task == 'GSM':
            messages.append({"role":"user","content":FS_CoT_GSM.format(problem=problem)})
        elif task == 'HQA':
            messages.append({"role":"user","content":FS_CoT_HQA.format(problem=problem)})
        elif task == "CMQA":
            messages.append({"role":"user","content":FS_CoT_CMQA.format(problem=problem)})
        elif task == 'MATHQA':
            messages.append({"role":"user","content":FS_CoT_MATHQA.format(problem=problem)})
        elif task == 'STRATEGYQA':
            messages.append({"role":"user","content":FS_CoT_STRATEGYQA.format(problem=problem)})
        elif task == 'MATH':
            messages.append({"role":"user","content":FS_CoT_MATH.format(problem=problem)})
    else:
        raise NotImplementedError(f"Required method for get answer: {method} is NOT implemented!")
    
    if mit_method == 'demonstration':
        messages[-1] = {"role":"user","content":FS_CoT_STRATEGYQA_MIT.format(problem=problem)}
    elif mit_method == 'repeat':
        messages[-1]['content'] = messages[-1]['content'] + ANSWER_RESTATE
        
    if attack == 0:
        #print(f'NO ATT\n{raw}')
        if method == 'ZS':
            raw = chat(messages)
            ans=clean_response(raw,task)
        else:
            raw = chat(messages, temperature, top_p)
            ans=get_final_answer(raw,task=task,problem=problem,attack=attack)
        #print(f'NO ATT[Processed]\n{ans}')
    elif attack==1: # answer first attack
        messages[-1]['content'] = messages[-1]['content'] + " " + ANSWER_FIRST
        raw=chat(messages, temperature, top_p)
        # print(f'ATT1\n{raw}')
        ans=get_final_answer(raw,task=task,problem=problem,attack=attack)
        # print(f'ATT1[Processed] {ans}')
    elif attack==2: # inject attack
        messages.append({"role":"user","content":ANSWER_INJECT.format(answer=wrong_answer)})
        raw=chat(messages, temperature, top_p)
        # print(f'ATT2\n{raw}')
        ans=get_final_answer(raw,task=task,problem=problem,attack=attack)
        # print(f'ATT2[Processed] {ans}')
    else:
        raise NotImplementedError(f"Required attack for get answer: {attack} is NOT implemented!")
    return ans, raw
        


# return a list of passed samples that is both answered correctly using CoT and incorrectly using ZS
def pretest(data,task,method):
    passed_check=[]
    num = 0    
    if method == 'ZS_CoT':
        for item in tqdm(data):
            question = item['question']
            gold_answer = item['answer']
            # ZS_Answer, _ = get_answer(problem=question,task=task,method='ZS')
            # is_correct_ZS = check_answer(bot_answer=ZS_Answer,gold_answer=gold_answer,task=task)
            # if is_correct_ZS:
            #     num += 1
            #     continue
            ZS_CoT_Answer, raw = get_answer(problem=question,task=task,method='ZS_CoT')
            is_correct_ZS_CoT = check_answer(bot_answer=ZS_CoT_Answer ,gold_answer=gold_answer,task=task)
            item['pretest'] = {'ZS_CoT_Answer':ZS_CoT_Answer, 'ZS_CoT_raw':raw}
            passed_check.append(item)
    elif method == 'FS_CoT':
        for item in tqdm(data):
            question = item['question']
            gold_answer = item['answer']
            # ZS_Answer, _ = get_answer(problem=question,task=task,method='ZS')
            # is_correct_ZS = check_answer(bot_answer=ZS_Answer,gold_answer=gold_answer,task=task)
            # if is_correct_ZS:
            #     num += 1
            #     continue
            FS_CoT_Answer, raw = get_answer(problem=question,task=task,method='FS_CoT')
            is_correct_FS_CoT = check_answer(bot_answer=FS_CoT_Answer ,gold_answer=gold_answer,task=task)
            item['pretest'] = {'FS_CoT_Answer':FS_CoT_Answer, 'FS_CoT_raw':raw}
            passed_check.append(item)
    elif method == 'SC_FS_CoT':
        for item in tqdm(data):
            question = item['question']
            gold_answer = item['answer']
            # ZS_Answer, _ = get_answer(problem=question,task=task,method='ZS')
            # is_correct_ZS = check_answer(bot_answer=ZS_Answer,gold_answer=gold_answer,task=task)
            # if is_correct_ZS:
            #     num += 1
            #     continue
            all_FS_CoT_Answer = []
            for n in range(NUM_SC):
                FS_CoT_Answer, _ = get_answer(problem=question,task=task,method='FS_CoT')
                all_FS_CoT_Answer.append(FS_CoT_Answer)
            FS_CoT_Answer = find_most_frequent(all_FS_CoT_Answer)
            is_correct_FS_CoT = check_answer(bot_answer=FS_CoT_Answer ,gold_answer=gold_answer,task=task)
            item['pretest'] = {'FS_CoT_Answer':FS_CoT_Answer, 'all_FS_CoT_Answer':all_FS_CoT_Answer}
            passed_check.append(item)
    elif method == 'SC_ZS_CoT':
        for item in tqdm(data):
            question = item['question']
            gold_answer = item['answer']
            # ZS_Answer, _ = get_answer(problem=question,task=task,method='ZS')
            # is_correct_ZS = check_answer(bot_answer=ZS_Answer,gold_answer=gold_answer,task=task)
            all_ZS_CoT_Answer = []
            for n in range(NUM_SC):
                ZS_CoT_Answer, _ = get_answer(problem=question,task=task,method='ZS_CoT')
                all_ZS_CoT_Answer.append(ZS_CoT_Answer)
            # print(all_ZS_CoT_Answer, type(all_ZS_CoT_Answer))
            ZS_CoT_Answer = find_most_frequent(all_ZS_CoT_Answer)
            is_correct_ZS_CoT = check_answer(bot_answer=ZS_CoT_Answer ,gold_answer=gold_answer,task=task)
            item['pretest'] = {'ZS_CoT_Answer':ZS_CoT_Answer, 'all_ZS_CoT_Answer':all_ZS_CoT_Answer}
            passed_check.append(item)
    else:
        raise NotImplementedError(f"Required task for pretest: {task} is NOT implemented!")
    print(num)
    return passed_check

def reflection(problem, raw, task, attack=0):
    messages=[]
    messages.append({"role":"system","content":SYS})        
    messages.append({'role': 'assistant', "content": SELFCHECK.format(problem=problem, rationale=raw)})
    raw=chat(messages, temperature, top_p)
    # print(f'reflect\n{raw}')
    ans=get_final_answer(raw,task=task,problem=problem,attack=0)
    # print(f'reflect[Processed] {ans}')
    return ans, raw

def mit_reflection(data,task,method):
    after_reflection = []
    for item in tqdm(data):
        question = item['question']
        gold_answer = item['answer']
        
        Answer_1 = item['attack']['ATT_1']
        raw_1 = item['attack']['ATT_1_raw']
        answer_1_new, raw_1_new = reflection(question, raw_1, task)
        
        Answer_2 = item['attack']['ATT_2']
        raw_2 = item['attack']['ATT_2_raw']
        answer_2_new, raw_2_new = reflection(question, raw_2, task)
        
        item['attack'] = {'ATT_1':answer_1_new, 'ATT_2':answer_2_new, 'ATT_1_raw':raw_1_new, 'ATT_2_raw':raw_2_new}
        after_reflection.append(item)
    return after_reflection

# run attack
def attack(data,task,method):
    result = []
    if method == 'ZS_CoT':
        for item in tqdm(data):
            question = item['question']
            wrong_answer = item['wrong_answer']
            ATT_1, ATT_1_raw = get_answer(problem=question,method=method,task=task,attack=1, mit_method='repeat')
            ATT_2, ATT_2_raw = get_answer(problem=question,method=method,task=task,attack=2,wrong_answer=wrong_answer,mit_method='repeat')
            item['attack'] = {'ATT_1':ATT_1,'ATT_2':ATT_2, 'ATT_1_raw':ATT_1_raw, 'ATT_2_raw':ATT_2_raw}
            result.append(item)
    elif method == 'FS_CoT':
        for item in tqdm(data):
            question = item['question']
            wrong_answer = item['wrong_answer']
            ATT_1, ATT_1_raw = get_answer(problem=question,method=method,task=task,attack=1,mit_method='repeat')
            ATT_2, ATT_2_raw = get_answer(problem=question,method=method,task=task,attack=2,wrong_answer=wrong_answer,mit_method='repeat')
            item['attack'] = {'ATT_1':ATT_1,'ATT_2':ATT_2, 'ATT_1_raw':ATT_1_raw, 'ATT_2_raw':ATT_2_raw}
            result.append(item)
    elif method == 'SC_ZS_CoT':
        for item in tqdm(data):
            question = item['question']
            wrong_answer = item['wrong_answer']
            all_ATT_1_answers = []
            all_ATT_2_answers = []
            for n in range(NUM_SC):
                ATT_1, ATT_1_raw = get_answer(problem=question,method=method,task=task,attack=1)
                ATT_2, ATT_2_raw = get_answer(problem=question,method=method,task=task,attack=2,wrong_answer=wrong_answer)
                all_ATT_1_answers.append(ATT_1)
                all_ATT_2_answers.append(ATT_2)
            ATT_1 = find_most_frequent(all_ATT_1_answers)
            ATT_2 = find_most_frequent(all_ATT_2_answers)
            item['attack'] = {'ATT_1':ATT_1,'ATT_2':ATT_2}
            result.append(item)
    elif method == 'SC_FS_CoT':
        for item in tqdm(data):
            question = item['question']
            wrong_answer = item['wrong_answer']
            all_ATT_1_answers = []
            all_ATT_2_answers = []
            for n in range(NUM_SC):
                ATT_1, ATT_1_raw = get_answer(problem=question,method=method,task=task,attack=1)
                ATT_2, ATT_2_raw = get_answer(problem=question,method=method,task=task,attack=2,wrong_answer=wrong_answer)
                all_ATT_1_answers.append(ATT_1)
                all_ATT_2_answers.append(ATT_2)
            ATT_1 = find_most_frequent(all_ATT_1_answers)
            ATT_2 = find_most_frequent(all_ATT_2_answers)
            item['attack'] = {'ATT_1':ATT_1,'ATT_2':ATT_2}
            result.append(item)
    else:
        raise NotImplementedError(f"Required task for attack: {task} is NOT implemented!")
    return result

def compute_ACC(file, task, is_attak=False):
    data = []
    with open(file,'r') as infile:
        for line in infile:
            data.append(json.loads(line))
    
    if is_attak == True:
        num=len(data)
        num_correct_1 = 0
        num_correct_2 = 0
        for item in data:
            gold_answer = item['answer']
            att_1 = item['attack']['ATT_1']
            att_2 = item['attack']['ATT_2']
            if check_answer(bot_answer=att_1,gold_answer=gold_answer,task=task):
                num_correct_1 += 1
            if check_answer(bot_answer=att_2,gold_answer=gold_answer,task=task):
                num_correct_2 += 1
        
        acc_1 = num_correct_1/num*100
        acc_2 = num_correct_2/num*100
        print(f'ACC (%) for attack 1: {acc_1:.4f}')
        print(f'ACC (%) for attack 2: {acc_2:.4f}')
    else:
        num=len(data)
        num_correct = 0
        if 'ZS_CoT' in file:
            test_method = 'ZS_CoT'
        if 'FS_CoT' in file:
            test_method = 'FS_CoT'
        for item in data:
            gold_answer = item['answer']
            bot_answer = item['pretest'][test_method + '_Answer']
            if check_answer(bot_answer=bot_answer,gold_answer=gold_answer,task=task):
                num_correct += 1
        acc = num_correct/num*100
        print(f'ACC (%) for original: {acc:.4f}')


def compute_ASR(file, task):
    data = []
    with open(file,'r') as infile:
        for line in infile:
            data.append(json.loads(line))
    
    new_data = []
    # data = data[:100]
    for item in data:
        if 'ZS_CoT' in file:
            test_method = 'ZS_CoT'
        if 'FS_CoT' in file:
            test_method = 'FS_CoT'
        gold_answer = item['answer']
        bot_answer = item['pretest'][test_method + '_Answer']
        if check_answer(bot_answer=bot_answer,gold_answer=gold_answer,task=task):
            new_data.append(item)
    
    data = new_data 
    num=len(data)
    print(num)
    num_wrong_1 = 0
    num_wrong_2 = 0
    for item in data:
        gold_answer = item['answer']
        att_1 = item['attack']['ATT_1']
        att_2 = item['attack']['ATT_2']
        if not check_answer(bot_answer=att_1,gold_answer=gold_answer,task=task):
            num_wrong_1 += 1
        if not check_answer(bot_answer=att_2,gold_answer=gold_answer,task=task):
            num_wrong_2 += 1
    asr_1 = num_wrong_1/num*100
    asr_2 = num_wrong_2/num*100
    print(f'ASR (%) for attack 1: {asr_1:.4f}')
    print(f'ASR (%) for attack 2: {asr_2:.4f}')

def is_consistency(file, task):
    data = []
    with open(file,'r') as infile:
        for line in infile:
            data.append(json.loads(line))
            
    num=len(data)
    attack1_consistency = 0
    attack1_consistency_correct_correct = 0
    attack1_consistency_incorrect_incorrect = 0
    attack1_inconsistency = 0
    attack1_inconsistency_correct_incorrect = 0
    attack1_inconsistency_incorrect_correct = 0
    attack2_consistency = 0
    attack2_inconsistency = 0
    attack2_correct = 0
    
    for item in data:
        gold_answer = item['answer']
        wrong_answer = item['wrong_answer']
        if task == 'GSM':
            wrong_answer = '#### ' + wrong_answer[-1]
        raw_attack1 = item['attack']['ATT_1_raw']
        if '[Answer]\n' in raw_attack1:
            idx = raw_attack1.find('[Answer]\n')
            raw_attack1 = raw_attack1[:idx] + '[Answer] ' + raw_attack1[idx + len('[Answer]\n'):]
        if '[Answer]\n' in raw_attack1:
            idx = raw_attack1.find('[Answer]\n')
            raw_attack1 = raw_attack1[:idx] + '[Answer] ' + raw_attack1[idx + len('[Answer]\n'):]
        raw_attack1_texts = raw_attack1.strip().split('\n')
        for text in raw_attack1_texts:
            if '[answer]' in text.lower():
                raw_attack1 = text
                break
        attack1_pre = clean_response(raw_attack1, task)
        if task == "GSM":
            if attack1_pre != '':
                attack1_pre = '#### ' + attack1_pre[-1]
        attack1_ans = item['attack']['ATT_1']
        attack2_ans = item['attack']['ATT_2']
        
        if check_answer(gold_answer=attack1_pre, bot_answer=attack1_ans, task=task):
            attack1_consistency += 1
            if check_answer(gold_answer=gold_answer, bot_answer=attack1_ans, task=task):
                attack1_consistency_correct_correct += 1
            else:
                attack1_consistency_incorrect_incorrect += 1
        else:
            attack1_inconsistency += 1
            before = check_answer(gold_answer=gold_answer, bot_answer=attack1_pre, task=task)
            after = check_answer(gold_answer=gold_answer, bot_answer=attack1_ans, task=task)
            if before==True and after==False:
                attack1_inconsistency_correct_incorrect += 1
            else:
                attack1_inconsistency_incorrect_correct += 1
                
        if check_answer(gold_answer=wrong_answer, bot_answer=attack2_ans, task=task):
            attack2_consistency += 1
        else:
            attack2_inconsistency += 1
            if check_answer(gold_answer=gold_answer, bot_answer=attack2_ans, task=task):
                attack2_correct += 1
                
    print('ATT1=================')
    print('Consistency: {}, {}', attack1_consistency, attack1_consistency / num)
    print('Inconsistency: {}, {}', attack1_inconsistency, attack1_inconsistency / num)
    print('Consistency Correct: {}, {}', attack1_consistency_correct_correct, attack1_consistency_correct_correct / attack1_consistency)
    print('Consistency Incorrect: {}, {}', attack1_consistency_incorrect_incorrect, attack1_consistency_incorrect_incorrect / attack1_consistency)
    print('Inconsistency Correct Incorrect: {}, {}', attack1_inconsistency_correct_incorrect, attack1_inconsistency_correct_incorrect / attack1_inconsistency)
    print('Inconsistency Incorrect Correct: {}, {}', attack1_inconsistency_incorrect_correct, attack1_inconsistency_incorrect_correct / attack1_inconsistency)
    print('ATT2================')
    print('Consistency: {}, {}', attack2_consistency, attack2_consistency / num)
    print('Inconsistency: {}, {}', attack2_inconsistency, attack2_inconsistency / num)
    print('Inconsistency Correct: {}, {}', attack2_correct, attack2_correct / attack2_inconsistency)

if __name__ == "__main__":

    tasks = ['GSM', 'MATHQA', 'MATH', 'HQA', 'CMQA', 'STRATEGYQA']
    # test_methods = ['SC_ZS_CoT', 'SC_FS_CoT']
    test_methods = ['ZS_CoT', 'FS_CoT']#, 'SC_ZS_CoT', 'SC_FS_CoT']
    mitigation_methods = ['repeat', 'demonstration', 'reflect']
    mit_method = mitigation_methods[0]
    
    # I. Pretest
    # for i in range(0, 1):#len(tasks)):
    #     for j in range(0, len(test_methods)):
    #         task = tasks[i]
    #         test_method = test_methods[j]
            
    #         if 'SC' in test_method:
    #             temperature=1
    #             top_p=1
    #         else:
    #             temperature=0
    #             top_p=0
                
    #         print('temperature', temperature)
    #         start_time = time.time()
    #         data_pretest = []
    #         with open(f'../dataset/{task}.jsonl', 'r') as infile:
    #             for line in infile:
    #                 data_pretest.append(json.loads(line))

    #         data_pretest=data_pretest[:100]
    #         split_data = np.array_split(data_pretest, cpu_count())
    #         split_data = [(split,task,test_method) for split in split_data]

    #         result=run_in_parallel_with_result(pretest,split_data,num_processes=len(split_data))

    #         result = [item for sublist in result for item in sublist]

    #         with open(f'../dataset/{task}_{test_method}_{mit_method}.jsonl', 'w') as outfile:
    #             for item in result:
    #                 json.dump(item, outfile)
    #                 outfile.write('\n')

    #         end_time = time.time()
    #         elapsed_time = (end_time - start_time)/60
    #         print(f'{len(result)} sample(s) passed the test! Time cost: {elapsed_time}.')
    
    # II. Original acc
    # for i in range(0, len(tasks)):
    #     for j in range(1):
    #         task = tasks[i]
    #         test_method = test_methods[j]
    #         print(task, test_method)
    #         compute_ACC(f'../dataset/{task}_{test_method}.jsonl',task=task)
    
    
    
    # III. Attack
    # mit_method = 'repeat'
    # for i in range(2, len(tasks)):
    #     for j in range(0, 2):
    #         task = tasks[i]
    #         test_method = test_methods[j]
            
    #         if 'SC' in test_method:
    #             temperature=1
    #             top_p=1
    #         else:
    #             temperature=0
    #             top_p=0
                
    #         print('temperature', temperature)
    #         start_time = time.time()
    #         data_attack = []
    #         with open(f'../dataset/{task}_{test_method}_1.jsonl','r') as infile:
    #             for line in infile:
    #                 data_attack.append(json.loads(line))

    #         data_attack=data_attack

    #         split_data = np.array_split(data_attack, cpu_count())
    #         split_data = [(split,task,test_method) for split in split_data]

    #         result = run_in_parallel_with_result(attack,split_data,num_processes=len(split_data))

    #         result = [item for sublist in result for item in sublist]

    #         with open(f'../results/{task}_{test_method}_{mit_method}.jsonl', 'w') as outfile:
    #             for item in result:
    #                 json.dump(item, outfile)
    #                 outfile.write('\n')

    #         end_time = time.time()
    #         elapsed_time = (end_time - start_time)/60
    #         print(f'Attack time cost: {elapsed_time}.')
    mit_method = 'reflect'
    for i in range(0, len(tasks)):
        for j in range(0, 2):#len(test_methods)):
            task = tasks[i]
            test_method = test_methods[j]
            print(task, test_method)
            compute_ACC(f'../results/{task}_{test_method}_{mit_method}.jsonl',task=task, is_attak=True)
            compute_ASR(f'../results/{task}_{test_method}_{mit_method}.jsonl',task=task)
            
    # IV reflection
    # mit_method = 'reflect'
    # for i in range(2, len(tasks)):
    #     for j in range(0, 2):
    #         task = tasks[i]
    #         test_method = test_methods[j]
            
    #         if 'SC' in test_method:
    #             temperature=1
    #             top_p=1
    #         else:
    #             temperature=0
    #             top_p=0
                
    #         print('temperature', temperature)
    #         start_time = time.time()
    #         data_attack = []
    #         with open(f'../results/{task}_{test_method}.jsonl','r') as infile:
    #             for line in infile:
    #                 data_attack.append(json.loads(line))

    #         data_attack=data_attack

    #         split_data = np.array_split(data_attack, cpu_count())
    #         split_data = [(split,task,test_method) for split in split_data]

    #         result = run_in_parallel_with_result(mit_reflection,split_data,num_processes=len(split_data))

    #         result = [item for sublist in result for item in sublist]
    #         with open(f'../results/{task}_{test_method}_{mit_method}.jsonl', 'w') as outfile:
    #             for item in result:
    #                 json.dump(item, outfile)
    #                 outfile.write('\n')
