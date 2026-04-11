import json

def compute_f1(true_set: set, pred_set: set) -> float:
    """Computes F1 score from true labels vs predicted labels."""
    if not true_set and not pred_set:
        return 1.0 # Both empty means perfect match
    if not true_set or not pred_set:
        return 0.0
        
    intersection = len(true_set.intersection(pred_set))
    precision = intersection / len(pred_set)
    recall = intersection / len(true_set)
    
    if precision + recall == 0:
        return 0.0
        
    return 2 * (precision * recall) / (precision + recall)

def evaluate_parser_accuracy(ground_truth_json: dict, extracted_json: dict) -> dict:
    """
    Simulates the evaluation step comparing extracted JSON to ground truth labels 
    and computes the overall F1 Score across fields like skills.
    Target: F1 >= 0.88.
    """
    
    # Example evaluation focusing heavily on skills matching (most critical for matching engine)
    true_skills = set(s.strip().lower() for s in ground_truth_json.get("skills", []))
    pred_skills = set(s.strip().lower() for s in extracted_json.get("skills", []))
    
    skills_f1 = compute_f1(true_skills, pred_skills)
    
    # Simplified boolean checks for other fields
    name_match = 1.0 if ground_truth_json.get("name") == extracted_json.get("name") else 0.0
    email_match = 1.0 if ground_truth_json.get("email") == extracted_json.get("email") else 0.0
    
    # Aggregate F1 (Weighted: 60% skills, 40% personal info)
    overall_f1 = (skills_f1 * 0.6) + (((name_match + email_match) / 2) * 0.4)
    
    report = {
        "skills_f1": round(skills_f1, 3),
        "name_accuracy": name_match,
        "email_accuracy": email_match,
        "overall_f1_score": round(overall_f1, 3),
        "target_met": overall_f1 >= 0.88
    }
    
    return report

if __name__ == "__main__":
    sample_truth = {"name": "John Doe", "email": "john@test.com", "skills": ["Python", "SQL", "AWS"]}
    sample_pred = {"name": "John Doe", "email": "john@test.com", "skills": ["Python", "AWS", "Docker"]}
    
    print("Running sample evaluation...")
    report = evaluate_parser_accuracy(sample_truth, sample_pred)
    print(json.dumps(report, indent=2))
    
    if report["target_met"]:
        print("Success! F1 >= 0.88 target achieved.")
    else:
        print("Failed to meet F1 target.")
