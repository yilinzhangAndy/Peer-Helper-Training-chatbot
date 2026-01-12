---
pipeline_tag: text-classification
tags:
- text-classification
- intent-classification
- roberta
library_name: transformers
---

# MAE Intent Classification Model

This model classifies student-advisor conversation intents in the Mechanical and Aerospace Engineering (MAE) domain.

## Model Details

- **Model Type**: RoBERTa-based text classification
- **Task**: Text Classification / Intent Classification
- **Number of Labels**: 5

## Intent Categories

The model classifies conversations into 5 intent categories:

1. **Exploration and Reflection** - Self-reflection, career exploration, personal growth
2. **Feedback and Support** - Seeking encouragement, emotional support, validation
3. **Goal Setting and Planning** - Academic planning, career planning, course selection
4. **Problem Solving and Critical Thinking** - Problem-solving, analytical thinking, troubleshooting
5. **Understanding and Clarification** - Seeking explanations, clarification, information

## Usage

### Using Hugging Face Inference API

```python
import requests

API_URL = "https://api-inference.huggingface.co/models/zylandy/mae-intent-classifier"
headers = {"Authorization": "Bearer YOUR_TOKEN"}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

output = query({
    "inputs": "I want to learn about research opportunities",
})
```

### Using Transformers

```python
from transformers import pipeline

classifier = pipeline("text-classification", model="zylandy/mae-intent-classifier")
result = classifier("I want to learn about research opportunities")
```

## Model Files

The model files are located in the `checkpoint-3146/` directory:
- `config.json` - Model configuration
- `model.safetensors` - Model weights
- `tokenizer_config.json` - Tokenizer configuration
- `vocab.json` - Vocabulary
- `merges.txt` - BPE merges
- `special_tokens_map.json` - Special tokens mapping

## Training

This model was fine-tuned on a balanced dataset of student-advisor conversations in the MAE domain.

## Citation

If you use this model, please cite:

```bibtex
@model{mae-intent-classifier,
  author = {Your Name},
  title = {MAE Intent Classification Model},
  year = {2025}
}
```
