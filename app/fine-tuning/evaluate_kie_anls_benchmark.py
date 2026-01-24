import os
import json
from collections import defaultdict


def levenshtein_distance(s1, s2):
    """
    Calculates the Levenshtein distance (edit distance) between two strings.
    The Levenshtein distance is the minimum number of single-character edits
    (insertions, deletions, or substitutions) required to change one string into the other.

    Args:
        s1 (str): The first string.
        s2 (str): The second string.

    Returns:
        int: The Levenshtein distance between s1 and s2.
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def normalized_levenshtein_similarity(val1, val2):
    """
    Calculates a normalized Levenshtein similarity score between two values.
    For boolean values, it performs an exact match. For other types, it converts them to strings
    and computes the similarity based on the Levenshtein distance. The score ranges from 0.0 (no similarity) to 1.0 (exact match).

    Args:
        val1: The first value to compare.
        val2: The second value to compare.

    Returns:
        float: The normalized similarity score (0.0 to 1.0).
    """
    # Handle booleans with strict equality
    if isinstance(val1, bool) and isinstance(val2, bool):
        return 1.0 if val1 == val2 else 0.0

    # Convert non-boolean values to strings for comparison
    def to_str(val):
        if val is None:
            return ""
        return str(val)

    s1 = to_str(val1)
    s2 = to_str(val2)

    if not s1 and not s2:
        return 1.0  # Both are empty (or None), considered a perfect match
    if not s1 or not s2:
        return 0.0  # One is empty, the other is not

    distance = levenshtein_distance(s1, s2)
    max_length = max(len(s1), len(s2))
    return 1.0 - (distance / max_length)


def calculate_anls(gt_folder, pred_folder, mismatch_save_path=None, exclude_fields=None, exclude_subfolders=None):
    """
    Calculates the Average Normalized Levenshtein Similarity (ANLS) for evaluating
    Key Information Extraction (KIE) or OCR results. It compares predicted JSON files
    against ground truth (GT) JSON files, with support for excluding specific fields or subfolders.

    Args:
        gt_folder (str): Path to the root folder containing ground truth data.
        pred_folder (str): Path to the root folder containing predicted data.
        mismatch_save_path (str, optional): Path to save a JSON file detailing all mismatches.
            If None, saves to 'mismatches.json' in pred_folder. Defaults to None.
        exclude_fields (list, optional): List of field names to exclude from evaluation. Defaults to None.
        exclude_subfolders (list, optional): List of subfolder names to exclude from evaluation. Defaults to None.

    Returns:
        tuple: A tuple containing:
            - results (dict): Detailed ANLS statistics per subfolder and field.
            - mismatches (list): List of dictionaries detailing each mismatch.
            - matched_files_count (int): Number of successfully processed file pairs.
    """
    mismatches = []
    exclude_fields = exclude_fields if exclude_fields is not None else []
    exclude_subfolders = exclude_subfolders if exclude_subfolders is not None else []
    matched_files_count = 0

    results = defaultdict(lambda: {
        "total_anls": 0.0,
        "field_count": 0,
        "fields": defaultdict(lambda: {"total_anls": 0.0, "count": 0})
    })

    # Get all subfolders in GT folder, excluding specified ones
    all_subfolders = [f for f in os.listdir(gt_folder)
                      if os.path.isdir(os.path.join(gt_folder, f))
                      and f not in exclude_subfolders]

    for subfolder in all_subfolders:
        gt_json_path = os.path.join(gt_folder, subfolder, "json")
        pred_json_path = os.path.join(pred_folder, subfolder, "predict")

        if not os.path.isdir(gt_json_path):
            print(f"Warning: GT JSON subfolder does not exist - {gt_json_path}")
            continue
        if not os.path.isdir(pred_json_path):
            print(f"Warning: Prediction JSON subfolder does not exist - {pred_json_path}")
            continue

        # Get list of JSON files in both GT and prediction folders
        gt_files = {f for f in os.listdir(gt_json_path) if f.endswith('.json')}
        pred_files = {f for f in os.listdir(pred_json_path) if f.endswith('.json')}

        # Process only files that exist in both
        common_files = gt_files & pred_files
        if not common_files:
            print(f"Warning: No matching JSON files found in subfolder {subfolder}")
            continue

        for filename in common_files:
            gt_file_path = os.path.join(gt_json_path, filename)
            pred_file_path = os.path.join(pred_json_path, filename)

            try:
                with open(gt_file_path, 'r', encoding='utf-8') as f:
                    gt_data = json.load(f)
                with open(pred_file_path, 'r', encoding='utf-8') as f:
                    pred_data = json.load(f)
            except Exception as e:
                print(f"Error reading file {filename}: {e}")
                continue

            # Process GT data
            gt_raw = gt_data.get('output', {})
            if isinstance(gt_raw, dict):
                gt_result = gt_raw
                comparison_mode = "dict"
            else:
                gt_result = {"content": gt_raw}
                comparison_mode = "str"

            # Process Prediction data
            if subfolder == "non-semantic-text-ocr-20k":
                pred_raw = pred_data.get('result', {}).get('content', "")
            else:
                pred_raw = pred_data.get('result', {})

            if not isinstance(pred_raw, dict):
                pred_result = {"content": pred_raw}
            else:
                pred_result = pred_raw

            matched_files_count += 1
            # Optional: Uncomment the line below for verbose processing output
            # print(f"Processing file: {filename} (Mode: {comparison_mode})")

            # Calculate ANLS for each field
            for field, gt_value in gt_result.items():
                if field in exclude_fields:
                    continue

                gt_original = gt_value
                pred_original = pred_result.get(field)

                anls = normalized_levenshtein_similarity(gt_original, pred_original)

                if anls < 1.0:
                    mismatches.append({
                        "subfolder": subfolder,
                        "filename": filename,
                        "field": field,
                        "groundtruth": gt_original,
                        "prediction": pred_original,
                        "similarity": round(anls, 4),
                        "mode": comparison_mode
                    })

                # Update statistics
                results[subfolder]["total_anls"] += anls
                results[subfolder]["field_count"] += 1
                results[subfolder]["fields"][field]["total_anls"] += anls
                results[subfolder]["fields"][field]["count"] += 1

    # Save mismatches report
    save_path = mismatch_save_path or os.path.join(pred_folder, "mismatches.json")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(mismatches, f, ensure_ascii=False, indent=2)
    print(f"\nMismatch details saved to: {save_path}")

    # Print summary statistics
    print(f"\nSuccessfully processed {matched_files_count} matching JSON file pairs.")

    print("\nSubfolder-level ANLS:")
    for subfolder, stats in sorted(results.items()):
        if stats["field_count"] > 0:
            anls = stats["total_anls"] / stats["field_count"]
            print(f"{subfolder}: {anls * 100:.2f}% (Field count: {stats['field_count']})")

    total_anls = sum(stats["total_anls"] for stats in results.values())
    total_fields = sum(stats["field_count"] for stats in results.values())
    overall_anls = total_anls / total_fields if total_fields > 0 else 0.0

    print(f"\nOverall ANLS: {overall_anls * 100:.2f}% (Total fields evaluated: {total_fields})")

    return results, mismatches, matched_files_count


if __name__ == "__main__":
    # Configuration - Please update these paths
    GT_FOLDER = r"<PATH_TO_GROUND_TRUTH_ROOT_FOLDER>"
    PREDICT_FOLDER = r"<PATH_TO_PREDICTION_ROOT_FOLDER>"
    OUTPUT_FOLDER = r"<PATH_TO_OUTPUT_FOLDER>"

    MISMATCH_REPORT_PATH = os.path.join(OUTPUT_FOLDER, "kie_evaluation_mismatches.json")

    # Fields to exclude from evaluation (e.g., fields that are not predicted)
    EXCLUDE_FIELDS = ["证书名称"]  # Example: ["Certificate Name"]

    # Subfolders to exclude from evaluation
    EXCLUDE_SUBFOLDERS = ["LayoutLLM_CORD", "LayoutLLM_FUNSD", "LayoutLLM_SROIE"]

    # Validate input folders
    if not os.path.exists(GT_FOLDER) or not os.path.exists(PREDICT_FOLDER):
        print("Error: One or more input folders do not exist. Please check the paths.")
        exit()

    # Calculate ANLS and generate reports
    calculate_anls(
        GT_FOLDER,
        PREDICT_FOLDER,
        MISMATCH_REPORT_PATH,
        exclude_fields=EXCLUDE_FIELDS,
        exclude_subfolders=EXCLUDE_SUBFOLDERS
    )