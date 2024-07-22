from run import *
import json
from prompt import *
from utils import *
from math_utils import *

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
        print(num, num_correct_1, num_correct_2)
        print(f'ACC (%) for attack 1: {acc_1:.4f}')
        print(f'ACC (%) for attack 2: {acc_2:.4f}')
    else:
        # data = data[:100]
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
        print(f'ACC (%) for original: {num_correct}, {acc:.4f}')


def compute_ASR(file, task):
    data = []
    with open(file,'r') as infile:
        for line in infile:
            data.append(json.loads(line))
    
    new_data = []
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
    print(len(data), num_wrong_1, num_wrong_2)
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