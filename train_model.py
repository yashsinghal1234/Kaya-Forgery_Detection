"""
Training Script for ML Code Analyzer
Train the model to detect AI-generated code
"""
from ml_code_analyzer import MLCodeAnalyzer
import os
import sys
import json

try:
    from datasets import load_dataset
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False


def check_dataset():
    """Check if dataset has enough samples"""
    dataset_path = 'datasets/training'
    
    human_path = os.path.join(dataset_path, 'human_written')
    ai_path = os.path.join(dataset_path, 'ai_generated')
    
    human_count = 0
    ai_count = 0
    
    if os.path.exists(human_path):
        for root, dirs, files in os.walk(human_path):
            human_count += len([f for f in files if f.endswith(('.py', '.js', '.java', '.cpp', '.cs'))])
    
    if os.path.exists(ai_path):
        for root, dirs, files in os.walk(ai_path):
            ai_count += len([f for f in files if f.endswith(('.py', '.js', '.java', '.cpp', '.cs'))])
    
    print(f"\n{'='*60}")
    print(f"Dataset Status:")
    print(f"  Human-written samples: {human_count}")
    print(f"  AI-generated samples: {ai_count}")
    print(f"  Total samples: {human_count + ai_count}")
    print(f"{'='*60}\n")
    
    if human_count < 10 or ai_count < 10:
        print("[!] WARNING: Dataset too small for training!")
        print("[!] Recommended: At least 100 samples per category")
        print("[!] Minimum: 10 samples per category")
        print()
        
        if human_count == 0 or ai_count == 0:
            print("[X] Cannot train with empty dataset!")
            print("\nTo add training data:")
            print(f"  1. Add human-written code to: {human_path}/")
            print(f"  2. Add AI-generated code to: {ai_path}/")
            print("  3. Organize by language (python/, javascript/, java/, etc.)")
            return False
    
    return True


def generate_sample_data():
    """Generate a few sample files for demonstration"""
    print("[*] Generating sample training data...")
    
    # Sample human-written code (typical patterns)
    human_sample = '''def calculate_total(items):
    total=0
    for item in items:
        if item['active']:
            total+=item['price']
    return total

def get_user(id):
    # find user
    users=load_users()
    for u in users:
        if u['id']==id:
            return u
    return None
'''
    
    # Sample AI-generated code (typical patterns)
    ai_sample = '''def calculate_total_price(items_list):
    """
    Calculate the total price of active items.
    
    Args:
        items_list: List of item dictionaries with 'active' and 'price' keys
        
    Returns:
        float: Total price of all active items
    """
    total_price = 0.0
    
    for item in items_list:
        if item.get('active', False):
            total_price += item.get('price', 0.0)
    
    return total_price


def get_user_by_id(user_id):
    """
    Retrieve a user by their unique identifier.
    
    Args:
        user_id: The unique identifier for the user
        
    Returns:
        dict: User object if found, None otherwise
    """
    users = load_users()
    
    for user in users:
        if user.get('id') == user_id:
            return user
    
    return None
'''
    
    # Create directories
    os.makedirs('datasets/training/human_written/python', exist_ok=True)
    os.makedirs('datasets/training/ai_generated/python', exist_ok=True)
    
    # Save samples
    with open('datasets/training/human_written/python/sample1.py', 'w') as f:
        f.write(human_sample)
    
    with open('datasets/training/ai_generated/python/sample1.py', 'w') as f:
        f.write(ai_sample)
    
    print("[+] Generated 2 sample files (1 human, 1 AI)")
    print("[!] Note: This is for demonstration only. Add more samples for real training!")


def _select_dataset_split(dataset_dict):
    if "train" in dataset_dict:
        return "train"
    if len(dataset_dict.keys()) > 0:
        return list(dataset_dict.keys())[0]
    return None


def _detect_code_field(sample):
    for key in ("code", "content", "text", "snippet"):
        if key in sample and isinstance(sample[key], str):
            return key
    return None


def _detect_label_field(sample):
    for key in ("label", "source", "is_ai", "ai_generated", "generated", "category"):
        if key in sample:
            return key
    return None


def _label_is_ai(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value == 1
    if isinstance(value, str):
        value_lower = value.strip().lower()
        if "ai" in value_lower or "generated" in value_lower:
            return True
        if "human" in value_lower:
            return False
    return None


def load_hf_dataset_python(max_samples_per_class=2000):
    """Load HF dataset and save python-only samples into training folders."""
    if not HF_AVAILABLE:
        print("[X] datasets library not installed. Add it to requirements.txt and install.")
        return False

    print("[*] Loading dataset basakdemirok/AIGCodeSet from Hugging Face...")
    try:
        dataset_dict = load_dataset("basakdemirok/AIGCodeSet")
    except Exception as exc:
        print(f"[X] Failed to load dataset: {exc}")
        print("[!] Make sure you are logged in: huggingface-cli login")
        return False

    split_name = _select_dataset_split(dataset_dict)
    if not split_name:
        print("[X] No dataset split found.")
        return False

    dataset = dataset_dict[split_name]
    if len(dataset) == 0:
        print("[X] Dataset split is empty.")
        return False

    sample = dataset[0]
    code_field = _detect_code_field(sample)
    label_field = _detect_label_field(sample)

    if not code_field or not label_field:
        print("[X] Could not detect code/label fields in dataset.")
        print(f"[!] Available keys: {list(sample.keys())}")
        return False

    lang_field = None
    for key in ("language", "lang"):
        if key in sample:
            lang_field = key
            break

    human_dir = os.path.join("datasets", "training", "human_written", "python")
    ai_dir = os.path.join("datasets", "training", "ai_generated", "python")
    os.makedirs(human_dir, exist_ok=True)
    os.makedirs(ai_dir, exist_ok=True)

    human_count = 0
    ai_count = 0

    print(f"[*] Using fields: code='{code_field}', label='{label_field}'")
    if lang_field:
        print(f"[*] Filtering by language field '{lang_field}' for python")
    else:
        print("[!] No language field found. Using all samples as python.")

    for idx, row in enumerate(dataset):
        if lang_field:
            lang_value = str(row.get(lang_field, "")).lower()
            if "python" not in lang_value:
                continue

        label_value = _label_is_ai(row.get(label_field))
        if label_value is None:
            continue

        code_text = row.get(code_field)
        if not isinstance(code_text, str) or not code_text.strip():
            continue

        if label_value:
            if max_samples_per_class and ai_count >= max_samples_per_class:
                continue
            ai_count += 1
            target_dir = ai_dir
            file_index = ai_count
            prefix = "ai"
        else:
            if max_samples_per_class and human_count >= max_samples_per_class:
                continue
            human_count += 1
            target_dir = human_dir
            file_index = human_count
            prefix = "human"

        file_path = os.path.join(target_dir, f"{prefix}_{file_index:05d}.py")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code_text)

        if max_samples_per_class and human_count >= max_samples_per_class and ai_count >= max_samples_per_class:
            break

    print(f"[+] Saved python samples: {human_count} human, {ai_count} AI")
    return human_count > 0 and ai_count > 0


def load_back3474_dataset(file_path, max_samples_per_class=None):
    """Load Back3474 AI/Human dataset JSON and save python samples."""
    if not os.path.exists(file_path):
        print(f"[X] Dataset file not found: {file_path}")
        return False

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as exc:
        print(f"[X] Failed to read dataset: {exc}")
        return False

    human_dir = os.path.join("datasets", "training", "human_written", "python")
    ai_dir = os.path.join("datasets", "training", "ai_generated", "python")
    os.makedirs(human_dir, exist_ok=True)
    os.makedirs(ai_dir, exist_ok=True)

    human_count = 0
    ai_count = 0

    for row in data:
        language = str(row.get("language", "")).lower()
        if "python" not in language:
            continue

        human_code = row.get("human_generated_code")
        if isinstance(human_code, str) and human_code.strip():
            if not max_samples_per_class or human_count < max_samples_per_class:
                human_count += 1
                file_path_out = os.path.join(human_dir, f"human_back_{human_count:05d}.py")
                with open(file_path_out, "w", encoding="utf-8") as f:
                    f.write(human_code)

        ai_code = row.get("ai_generated_code")
        if isinstance(ai_code, str) and ai_code.strip():
            if not max_samples_per_class or ai_count < max_samples_per_class:
                ai_count += 1
                file_path_out = os.path.join(ai_dir, f"ai_back_{ai_count:05d}.py")
                with open(file_path_out, "w", encoding="utf-8") as f:
                    f.write(ai_code)

        if max_samples_per_class and human_count >= max_samples_per_class and ai_count >= max_samples_per_class:
            break

    print(f"[+] Saved python samples from Back3474: {human_count} human, {ai_count} AI")
    return human_count > 0 and ai_count > 0


def main():
    print("""
╔═══════════════════════════════════════════════════════════╗
║         ML Code Analyzer - Training Script               ║
╚═══════════════════════════════════════════════════════════╝
""")
    
    # Optionally pull dataset from Hugging Face
    if HF_AVAILABLE:
        print("[?] Load Hugging Face dataset for Python training?")
        response = input("Load basakdemirok/AIGCodeSet? (y/n): ").strip().lower()
        if response == "y":
            limit_raw = input("Max samples per class (enter number or 'all'): ").strip().lower()
            if limit_raw in ("", "default"):
                max_samples = 2000
            elif limit_raw == "all":
                max_samples = None
            else:
                try:
                    max_samples = int(limit_raw)
                except ValueError:
                    print("[!] Invalid number. Using default of 2000.")
                    max_samples = 2000

            loaded = load_hf_dataset_python(max_samples_per_class=max_samples)
            if not loaded:
                print("[!] Hugging Face dataset load failed. Falling back to local dataset.")
    else:
        print("[!] datasets library not installed. Skipping Hugging Face dataset load.")

    # Optionally load Back3474 dataset
    back_path = os.path.join("datasets", "external", "ai_human_code.jsonl")
    if os.path.exists(back_path):
        print("[?] Load Back3474 AI/Human dataset for Python training?")
        response = input("Load Back3474 dataset? (y/n): ").strip().lower()
        if response == "y":
            limit_raw = input("Max samples per class (enter number or 'all'): ").strip().lower()
            if limit_raw in ("", "default"):
                max_samples = None
            elif limit_raw == "all":
                max_samples = None
            else:
                try:
                    max_samples = int(limit_raw)
                except ValueError:
                    print("[!] Invalid number. Using all samples.")
                    max_samples = None
            loaded = load_back3474_dataset(back_path, max_samples_per_class=max_samples)
            if not loaded:
                print("[!] Back3474 dataset load failed. Continuing with existing data.")

    # Check dataset
    if not check_dataset():
        print("\n[?] Would you like to generate sample training data for demonstration?")
        response = input("Generate samples? (y/n): ").strip().lower()
        
        if response == 'y':
            generate_sample_data()
            print("\n[!] Sample data generated. You can now train, but results will be limited.")
            print("[!] For production use, add at least 100+ samples per category.")
            print()
        else:
            print("[X] Training cancelled. Please add training data and try again.")
            return
    
    # Initialize analyzer
    print("[*] Initializing ML Code Analyzer...")
    analyzer = MLCodeAnalyzer()
    
    # Train
    print("\n[*] Starting training process...")
    print("[*] This may take a few minutes depending on dataset size...\n")
    
    success = analyzer.train()
    
    if success:
        print("\n" + "="*60)
        print("[✓] Training completed successfully!")
        print(f"[✓] Model saved to: models/code_detector_v1.pkl")
        print("="*60)
        print("\nNext steps:")
        print("  1. Test the model with: python test_ml_analyzer.py")
        print("  2. Use in production: The model will automatically load in code_analyzer.py")
        print()
    else:
        print("\n[X] Training failed. Please check the dataset and try again.")


if __name__ == '__main__':
    main()
