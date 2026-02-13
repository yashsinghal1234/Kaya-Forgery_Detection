# Kaya - AI Forgery Detection

Kaya analyzes images, PDFs, and source code to detect tampering and AI-generated content.

## Run the app

```powershell
python app.py
```

The app will re-exec into `.venv312` automatically if present.

## Train the code detector

```powershell
.\.venv312\Scripts\python train_model.py
```

## Datasets

This repo does not store training datasets. Download and place them locally as needed:

- Hugging Face: https://huggingface.co/datasets/basakdemirok/AIGCodeSet
- Back3474 GitHub dataset: https://github.com/Back3474/AI-Human-Generated-Program-Code-Dataset

After downloading, run `train_model.py` to populate `datasets/training` and retrain the model.

## Notes

- Generated artifacts (datasets, uploads, reports, temp files, and model pickles) are ignored by git.
- Documentation lives at `/documentation` in the running app.
