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
NUM_SC=3

def chat(messages):
    completion = chat_completion_with_backoff(
        model='gpt-3.5-turbo-0125',
        messages=messages,
        # max_tokens=4096,
        temperature=0,
        top_p=0
    )
    # print("OK")
    response = completion.choices[0].message.content.strip()
    return response


def check_answer(bot_answer,gold_answer,task):
    if task == 'GSM':
        gt_answer = extract_answer(gold_answer,task=task).lower()
        assert gt_answer != INVALID_ANS
        return gt_answer in bot_answer
    elif task == 'HQA':
        # print(f'Gold answer: {gold_answer}')
        # print(f'Bot answer: {bot_answer}')
        gt_answer = extract_answer(gold_answer,task=task).lower()
        assert gt_answer != INVALID_ANS
        return gt_answer in bot_answer
    elif task == 'CMQA':
        gt_answer = extract_answer(gold_answer,task=task).lower()
        # print(gt_answer, bot_answer)
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
    

def get_answer(problem,method,task,attack=0,wrong_answer=""):
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
    
    if attack == 0:
        raw = chat(messages)
        #print(f'NO ATT\n{raw}')
        if method == 'ZS':
            ans=clean_response(raw,task)
        else:
            ans=get_final_answer(raw,task=task,problem=problem,attack=attack)
        #print(f'NO ATT[Processed]\n{ans}')
    elif attack==1: # answer first attack
        messages[-1]['content'] = messages[-1]['content'] + " " + ANSWER_FIRST
        raw=chat(messages)
        # print(f'ATT1\n{raw}')
        ans=get_final_answer(raw,task=task,problem=problem,attack=attack)
        # print(f'ATT1[Processed] {ans}')
    elif attack==2: # inject attack
        messages.append({"role":"user","content":ANSWER_INJECT.format(answer=wrong_answer)})
        raw=chat(messages)
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
            ZS_Answer, _ = get_answer(problem=question,task=task,method='ZS')
            is_correct_ZS = check_answer(bot_answer=ZS_Answer,gold_answer=gold_answer,task=task)
            if is_correct_ZS:
                num += 1
                continue
            ZS_CoT_Answer, _ = get_answer(problem=question,task=task,method='ZS_CoT')
            is_correct_ZS_CoT = check_answer(bot_answer=ZS_CoT_Answer ,gold_answer=gold_answer,task=task)
            if is_correct_ZS_CoT: # ZS_CoT correct and ZS not correct
                item['pretest'] = {'ZS_Answer':ZS_Answer,'ZS_CoT_Answer':ZS_CoT_Answer}
                passed_check.append(item)
    elif method == 'FS_CoT':
        for item in tqdm(data):
            question = item['question']
            gold_answer = item['answer']
            ZS_Answer, _ = get_answer(problem=question,task=task,method='ZS')
            is_correct_ZS = check_answer(bot_answer=ZS_Answer,gold_answer=gold_answer,task=task)
            if is_correct_ZS:
                num += 1
                continue
            FS_CoT_Answer, _ = get_answer(problem=question,task=task,method='FS_CoT')
            is_correct_FS_CoT = check_answer(bot_answer=FS_CoT_Answer ,gold_answer=gold_answer,task=task)
            if is_correct_FS_CoT: # ZS_CoT correct and ZS not correct
                item['pretest'] = {'ZS_Answer':ZS_Answer,'FS_CoT_Answer':FS_CoT_Answer}
                passed_check.append(item)
    elif method == 'SC':
        for item in tqdm(data):
            question = item['question']
            gold_answer = item['answer']
            ZS_Answer, _ = get_answer(problem=question,task=task,method='ZS')
            is_correct_ZS = check_answer(bot_answer=ZS_Answer,gold_answer=gold_answer,task=task)
            if is_correct_ZS:
                num += 1
                continue
            all_FS_CoT_Answer = []
            for n in range(NUM_SC):
                FS_CoT_Answer, _ = get_answer(problem=question,task=task,method='FS_CoT')
                all_FS_CoT_Answer.append(FS_CoT_Answer)
            FS_CoT_Answer = find_most_frequent(all_FS_CoT_Answer)
            is_correct_FS_CoT = check_answer(bot_answer=FS_CoT_Answer ,gold_answer=gold_answer,task=task)
            if is_correct_FS_CoT: # ZS_CoT correct and ZS not correct
                item['pretest'] = {'ZS_Answer':ZS_Answer,'FS_CoT_Answer':FS_CoT_Answer}
                passed_check.append(item)
    else:
        raise NotImplementedError(f"Required task for pretest: {task} is NOT implemented!")
    print(num)
    return passed_check


# run attack
def attack(data,task,method):
    result = []
    if method == 'ZS_CoT':
        for item in tqdm(data):
            question = item['question']
            wrong_answer = item['pretest']['ZS_Answer']
            ATT_1, ATT_1_raw = get_answer(problem=question,method=method,task=task,attack=1)
            ATT_2, ATT_2_raw = get_answer(problem=question,method=method,task=task,attack=2,wrong_answer=wrong_answer)
            item['attack'] = {'ATT_1':ATT_1,'ATT_2':ATT_2, 'ATT_1_raw':ATT_1_raw, 'ATT_2_raw':ATT_2_raw}
            result.append(item)
    elif method == 'FS_CoT':
        for item in tqdm(data):
            question = item['question']
            wrong_answer = item['pretest']['ZS_Answer']
            ATT_1, ATT_1_raw = get_answer(problem=question,method=method,task=task,attack=1)
            ATT_2, ATT_2_raw = get_answer(problem=question,method=method,task=task,attack=2,wrong_answer=wrong_answer)
            item['attack'] = {'ATT_1':ATT_1,'ATT_2':ATT_2, 'ATT_1_raw':ATT_1_raw, 'ATT_2_raw':ATT_2_raw}
            result.append(item)
    elif method == 'SC':
        for item in tqdm(data):
            question = item['question']
            wrong_answer = item['pretest']['ZS_Answer']
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


def compute_ASR(file,task):
    data = []
    with open(file,'r') as infile:
        for line in infile:
            data.append(json.loads(line))
            
    num=len(data)
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



if __name__ == "__main__":

    tasks = ['GSM', 'HQA', 'CMQA', 'MATHQA', 'STRATEGYQA', 'MATH']
    test_methods = ['ZS_CoT', 'FS_CoT']

    task = tasks[5]
    test_method = test_methods[1]

    # I. Pretest
    # start_time = time.time()
    # data_pretest = []
    # with open(f'../dataset/{task}.jsonl', 'r') as infile:
    #     for line in infile:
    #         data_pretest.append(json.loads(line))

    # data_pretest=data_pretest
    # split_data = np.array_split(data_pretest, cpu_count())
    # split_data = [(split,task,test_method) for split in split_data]

    # result=run_in_parallel_with_result(pretest,split_data,num_processes=len(split_data))

    # result = [item for sublist in result for item in sublist]

    # with open(f'../dataset/{task}_{test_method}.jsonl', 'w') as outfile:
    #     for item in result:
    #         json.dump(item, outfile)
    #         outfile.write('\n')

    # end_time = time.time()
    # elapsed_time = (end_time - start_time)/60
    # print(f'{len(result)} sample(s) passed the test! Time cost: {elapsed_time}.')
    
    # II. Attack
    start_time = time.time()
    data_attack = []
    with open(f'../dataset/{task}_{test_method}.jsonl','r') as infile:
        for line in infile:
            data_attack.append(json.loads(line))

    data_attack=data_attack[:100]

    split_data = np.array_split(data_attack, cpu_count())
    split_data = [(split,task,test_method) for split in split_data]

    result = run_in_parallel_with_result(attack,split_data,num_processes=len(split_data))

    result = [item for sublist in result for item in sublist]

    with open(f'../results/{task}_{test_method}.jsonl', 'w') as outfile:
        for item in result:
            json.dump(item, outfile)
            outfile.write('\n')

    end_time = time.time()
    elapsed_time = (end_time - start_time)/60
    print(f'Attack time cost: {elapsed_time}.')

    compute_ASR(f'../results/{task}_{test_method}.jsonl',task=task)

