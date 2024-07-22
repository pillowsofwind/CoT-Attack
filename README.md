# CoT Attack

This is the repo of script for the ACL 2024 Findings paper: [Preemptive Answer" Attacks" on Chain-of-Thought Reasoning](https://arxiv.org/abs/2405.20902).

```
@article{xu2024preemptive,
  title={Preemptive Answer" Attacks" on Chain-of-Thought Reasoning},
  author={Xu, Rongwu and Qi, Zehan and Xu, Wei},
  journal={arXiv preprint arXiv:2405.20902},
  year={2024}
}
```

## Usage

- Step I. set up conda experiments using `pip intall -r requirements.txt` and your OpenAI API key in `utils.py`.

- Step II. run Pretest and Attack in `run.py`.

- Step III. run Pretest and Attack in `run.py` for self-consistency (SC) experiments.

- Step IV. run mitigation experiments in `mitigation.py`
