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


def calculate_anls(gt_folder, pred_folder, mismatch_save_path=None, exclude_fields=None):
    """
    Calculates the Average Normalized Levenshtein Similarity (ANLS) for evaluating
    the performance of a Key Information Extraction (KIE) model. It compares predicted
    JSON files against ground truth (GT) JSON files.

    Args:
        gt_folder (str): Path to the folder containing ground truth JSON files.
        pred_folder (str): Path to the folder containing predicted JSON files.
        mismatch_save_path (str, optional): Path to save a detailed JSON report of all mismatches.
            If None, saves to 'evaluation_results.json' in pred_folder. Defaults to None.
        exclude_fields (list, optional): List of field names to exclude from the evaluation.
            Defaults to None.

    Returns:
        tuple: A tuple containing two dictionaries:
            - results: Detailed statistics including ANLS per category and field.
            - final_results: A structured summary including overall ANLS, category-level ANLS,
                             field-level ANLS, and a list of all mismatches.
    """
    # Initialize list to record mismatches
    mismatches = []
    # Handle excluded fields, defaulting to an empty list
    exclude_fields = exclude_fields if exclude_fields is not None else []
    # Counter for successfully matched and processed file pairs
    matched_files_count = 0

    # Data structure to hold ANLS statistics
    results = defaultdict(lambda: {
        "total_anls": 0.0,
        "field_count": 0,
        "fields": defaultdict(lambda: {"total_anls": 0.0, "count": 0})
    })

    # Traverse all category folders
    for category in os.listdir(gt_folder):
        gt_category_path = os.path.join(gt_folder, category)
        pred_category_path = os.path.join(pred_folder, category)

        if not os.path.isdir(gt_category_path) or not os.path.isdir(pred_category_path):
            continue

        # Traverse all JSON files in the current category
        for filename in os.listdir(gt_category_path):
            if filename.endswith('.json'):
                gt_file_path = os.path.join(gt_category_path, filename)
                pred_file_path = os.path.join(pred_category_path, filename)

                # Ensure the prediction file exists
                if not os.path.exists(pred_file_path):
                    print(f"Warning: {pred_file_path} does not exist.")
                    continue

                # Read GT and prediction files
                try:
                    with open(gt_file_path, 'r', encoding='utf-8') as f:
                        gt_data = json.load(f)
                    with open(pred_file_path, 'r', encoding='utf-8') as f:
                        pred_data = json.load(f)
                except Exception as e:
                    print(f"Error reading file {filename}: {e}")
                    continue

                matched_files_count += 1

                # Extract the 'result' fields
                gt_result = gt_data.get('result', {})
                pred_result = pred_data.get('result', {})

                # Calculate ANLS for each field (excluding specified fields)
                for field, gt_value in gt_result.items():
                    if field in exclude_fields:
                        continue

                    # Save original values for reporting
                    gt_original = gt_value
                    pred_original = pred_result.get(field)

                    # Convert values to strings for comparison
                    gt_str = str(gt_value) if gt_value is not None else ""
                    pred_str = str(pred_original) if pred_original is not None else ""

                    # Calculate ANLS for this field
                    anls = normalized_levenshtein_similarity(gt_str, pred_str)

                    # Record mismatch if similarity is less than 1.0
                    if anls < 1.0:
                        mismatches.append({
                            "category": category,
                            "filename": filename,
                            "field": field,
                            "groundtruth": gt_original,
                            "prediction": pred_original,
                            "similarity": round(anls, 4)
                        })

                    # Update statistics
                    results[category]["total_anls"] += anls
                    results[category]["field_count"] += 1
                    results[category]["fields"][field]["total_anls"] += anls
                    results[category]["fields"][field]["count"] += 1

    # Calculate overall ANLS
    total_anls = sum(stats["total_anls"] for stats in results.values())
    total_fields = sum(stats["field_count"] for stats in results.values())
    overall_anls = total_anls / total_fields if total_fields > 0 else 0.0

    # Construct the final results dictionary
    final_results = {
        "overall_anls": round(overall_anls * 100, 2),
        "total_fields": total_fields,
        "matched_files_count": matched_files_count,
        "category_level_anls": {},
        "field_level_anls": {},
        "mismatches": mismatches
    }

    # Populate category-level ANLS
    for category, stats in results.items():
        if stats["field_count"] > 0:
            category_anls = stats["total_anls"] / stats["field_count"]
            final_results["category_level_anls"][category] = {
                "anls": round(category_anls * 100, 2),
                "field_count": stats["field_count"]
            }

            # Populate field-level ANLS
            for field, field_stats in stats["fields"].items():
                if field_stats["count"] > 0:
                    field_anls = field_stats["total_anls"] / field_stats["count"]
                    if field not in final_results["field_level_anls"]:
                        final_results["field_level_anls"][field] = []
                    final_results["field_level_anls"][field].append({
                        "category": category,
                        "anls": round(field_anls * 100, 2),
                        "count": field_stats["count"]
                    })

    # Save results to a JSON file
    save_path = mismatch_save_path or os.path.join(pred_folder, "evaluation_results.json")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(final_results, f, ensure_ascii=False, indent=2)
    print(f"\nFull evaluation results saved to: {save_path}")

    # Print summary results
    print(f"\nSuccessfully processed {matched_files_count} file pairs.")
    print("\nCategory-level ANLS:")
    for category, stats in sorted(final_results["category_level_anls"].items()):
        print(f"{category}: {stats['anls']:.2f}% (Field count: {stats['field_count']})")

    print("\nOverall ANLS: {:.2f}% (Total fields evaluated: {})".format(final_results["overall_anls"], total_fields))

    return results, final_results


if __name__ == "__main__":
    # Configuration
    GT_FOLDER = r"<PATH_TO_GROUND_TRUTH_FOLDER>"
    PREDICT_FOLDER = r"<PATH_TO_PREDICTION_FOLDER>"
    OUTPUT_FOLDER = r"<PATH_TO_OUTPUT_FOLDER>"

    RESULT_PATH = os.path.join(OUTPUT_FOLDER, "evaluation_results.json")

    # Fields to exclude from evaluation (e.g., fields that are not predicted)
    EXCLUDE_FIELDS = ["证书名称"]  # Example: ["Certificate Name", "School Name"]

    # Validate input folders
    if not os.path.exists(GT_FOLDER) or not os.path.exists(PREDICT_FOLDER):
        print("Error: One or more input folders do not exist. Please check the paths.")
        exit()

    # Calculate ANLS and save results
    calculate_anls(GT_FOLDER, PREDICT_FOLDER, RESULT_PATH, exclude_fields=EXCLUDE_FIELDS)