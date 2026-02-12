# Code Analysis ML Dataset Structure

## Directory Layout
```
datasets/
├── training/
│   ├── human_written/
│   │   ├── python/
│   │   ├── javascript/
│   │   ├── java/
│   │   ├── cpp/
│   │   └── csharp/
│   └── ai_generated/
│       ├── python/
│       ├── javascript/
│       ├── java/
│       ├── cpp/
│       └── csharp/
├── validation/
│   ├── human_written/
│   └── ai_generated/
└── test/
    ├── human_written/
    └── ai_generated/

models/
├── code_detector_v1.pkl         # Trained sklearn model
├── tokenizer/                    # Tokenizer for code
├── feature_extractor.pkl         # Feature extraction model
└── model_metadata.json           # Model training info
```

## Data Collection Sources

### Human-Written Code
- GitHub repositories (verified human authors)
- Open source projects
- Coding challenge submissions
- Academic assignments
- Professional codebases

### AI-Generated Code
- GPT-4 generated samples
- GitHub Copilot outputs
- ChatGPT code snippets
- Other AI coding assistants
- Synthetic variations

## Dataset Details
- **Minimum samples**: 10,000 per category (human/AI)
- **Balanced split**: 50% human, 50% AI
- **Languages**: Python, JavaScript, Java, C++, C#
- **Code length**: 50-500 lines per sample
- **Metadata**: author type, timestamp, source, language
