from openai import OpenAI       
import json
import requests 
from collections import Counter

client = OpenAI(
    api_key = ''
)

from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
) # for exponential backoff

## wait to avoid the limit
@retry(wait=wait_random_exponential(min=30, max=120), stop=stop_after_attempt(1000))
def chat_completion_with_backoff(**kwargs):
    return client.chat.completions.create(**kwargs)


from multiprocessing import Process, cpu_count

# 并行
def run_in_parallel(target_function, args_list):
    processes = []

    # 创建进程
    for args in args_list:
        proc = Process(target=target_function, args=(args,))
        processes.append(proc)
        proc.start()

    # 等待所有进程完成
    for proc in processes:
        proc.join()

import multiprocessing

def run_in_parallel_with_result(target_function, args_list, num_processes):
    # 使用进程池，指定进程数量
    with multiprocessing.Pool(processes=num_processes) as pool:
        # 使用map方法并行执行target_function
        results = pool.starmap(target_function, args_list)
    return results

""" Judgement for MATH """
def _fix_fracs(string):
    substrs = string.split("\\frac")
    new_str = substrs[0]
    if len(substrs) > 1:
        substrs = substrs[1:]
        for substr in substrs:
            new_str += "\\frac"
            if substr[0] == "{":
                new_str += substr
            else:
                try:
                    assert len(substr) >= 2
                except:
                    return string
                a = substr[0]
                b = substr[1]
                if b != "{":
                    if len(substr) > 2:
                        post_substr = substr[2:]
                        new_str += "{" + a + "}{" + b + "}" + post_substr
                    else:
                        new_str += "{" + a + "}{" + b + "}"
                else:
                    if len(substr) > 2:
                        post_substr = substr[2:]
                        new_str += "{" + a + "}" + b + post_substr
                    else:
                        new_str += "{" + a + "}" + b
    string = new_str
    return string

def _fix_a_slash_b(string):
    if len(string.split("/")) != 2:
        return string
    a = string.split("/")[0]
    b = string.split("/")[1]
    try:
        a = int(a)
        b = int(b)
        assert string == "{}/{}".format(a, b)
        new_string = "\\frac{" + str(a) + "}{" + str(b) + "}"
        return new_string
    except:
        return string

def _remove_right_units(string):
    # "\\text{ " only ever occurs (at least in the val set) when describing units
    if "\\text{ " in string:
        splits = string.split("\\text{ ")
        assert len(splits) == 2
        return splits[0]
    else:
        return string

def _fix_sqrt(string):
    if "\\sqrt" not in string:
        return string
    splits = string.split("\\sqrt")
    new_string = splits[0] 
    for split in splits[1:]:
        if split[0] != "{":
            a = split[0]
            new_substr = "\\sqrt{" + a + "}" + split[1:]
        else:
            new_substr = "\\sqrt" + split
        new_string += new_substr
    return new_string

def _strip_string(string):
    # linebreaks  
    string = string.replace("\n", "")
    #print(string)

    # remove inverse spaces
    string = string.replace("\\!", "")
    #print(string)

    # replace \\ with \
    string = string.replace("\\\\", "\\")
    #print(string)

    # replace tfrac and dfrac with frac
    string = string.replace("tfrac", "frac")
    string = string.replace("dfrac", "frac")
    #print(string)

    # remove \left and \right
    string = string.replace("\\left", "")
    string = string.replace("\\right", "")
    #print(string)
    
    # Remove circ (degrees)
    string = string.replace("^{\\circ}", "")
    string = string.replace("^\\circ", "")

    # remove dollar signs
    string = string.replace("\\$", "")
    
    # remove units (on the right)
    string = _remove_right_units(string)

    # remove percentage
    string = string.replace("\\%", "")
    string = string.replace("\%", "")

    # " 0." equivalent to " ." and "{0." equivalent to "{." Alternatively, add "0" if "." is the start of the string
    string = string.replace(" .", " 0.")
    string = string.replace("{.", "{0.")
    # if empty, return empty string
    if len(string) == 0:
        return string
    if string[0] == ".":
        string = "0" + string

    # to consider: get rid of e.g. "k = " or "q = " at beginning
    if len(string.split("=")) == 2:
        if len(string.split("=")[0]) <= 2:
            string = string.split("=")[1]

    # fix sqrt3 --> sqrt{3}
    string = _fix_sqrt(string)

    # remove spaces
    string = string.replace(" ", "")

    # \frac1b or \frac12 --> \frac{1}{b} and \frac{1}{2}, etc. Even works with \frac1{72} (but not \frac{72}1). Also does a/b --> \\frac{a}{b}
    string = _fix_fracs(string)

    # manually change 0.5 --> \frac{1}{2}
    if string == "0.5":
        string = "\\frac{1}{2}"

    # NOTE: X/Y changed to \frac{X}{Y} in dataset, but in simple cases fix in case the model output is X/Y
    string = _fix_a_slash_b(string)

    return string

def is_equiv(str1, str2, verbose=False):
    if str1 is None and str2 is None:
        print("WARNING: Both None")
        return True
    if str1 is None or str2 is None:
        return False

    try:
        ss1 = _strip_string(str1)
        ss2 = _strip_string(str2)
        if verbose:
            print(ss1, ss2)
        return ss1 == ss2
    except:
        return str1 == str2
    
def filter_choices(task, test_method):
    data_attack = []
    if task == 'STRATEGYQA':
        with open(f'../dataset/{task}_{test_method}.jsonl','r') as infile:
            for line in infile:
                line1 = json.loads(line)
                choice = line1['pretest']
                choice = choice['ZS_Answer']
                if choice != 'yes' and choice != 'no':
                    continue
                data_attack.append(json.loads(line))
                
        with open(f'../dataset/{task}_{test_method}_1.jsonl', 'w') as outfile:
            for item in data_attack:
                json.dump(item, outfile)
                outfile.write('\n')
    else:
        with open(f'../dataset/{task}_{test_method}.jsonl','r') as infile:
            for line in infile:
                line1 = json.loads(line)
                choice = line1['pretest']
                choice = choice['ZS_Answer']
                if choice != 'a' and choice != 'b' and choice != 'c' and choice != 'd' and choice != 'e':
                    continue
                data_attack.append(json.loads(line))
                
        with open(f'../dataset/{task}_{test_method}_1.jsonl', 'w') as outfile:
            for item in data_attack:
                json.dump(item, outfile)
                outfile.write('\n')
                
def find_most_frequent(strings):
    
    new_strings = []
    for string in strings:
        if isinstance(string, list):
            if isinstance(string[-1], list):
                new_strings.append(string[-1][-1])
            else:
                new_strings.append(string[-1])
        else:
            new_strings.append(string)
    
    # 计算每个字符串在列表中出现的次数
    counts = Counter(new_strings)
    # 找出出现次数最多的字符串及其次数
    most_common = counts.most_common(1)
    if most_common:
        # 返回出现次数最多的字符串
        return most_common[0][0]
    else:
        # 如果列表为空，返回None
        return None


        