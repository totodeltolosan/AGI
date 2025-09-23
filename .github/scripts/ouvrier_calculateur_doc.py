#!/usr/bin/env python3
"""
Handler Ouvrier Calculateur Documentation
Calcule des métriques sur la documentation extraite
"""

import json
import argparse
import sys

def calculate_documentation_metrics(facts_data):
    """Calcule les métriques de documentation."""
    metrics = {
        "coverage_ratio": 0.0,
        "quality_score": 0.0,
        "completeness": "incomplete",
        "recommendations": []
    }
    
    total_files = facts_data.get("total_files", 0)
    doc_files = facts_data.get("doc_files", 0)
    well_documented = len(facts_data.get("well_documented", []))
    
    if total_files > 0:
        metrics["coverage_ratio"] = round(doc_files / total_files, 2)
        metrics["quality_score"] = round(well_documented / total_files * 100, 1)
        
    if metrics["coverage_ratio"] >= 0.8:
        metrics["completeness"] = "excellent"
    elif metrics["coverage_ratio"] >= 0.6:
        metrics["completeness"] = "good"
    else:
        metrics["completeness"] = "poor"
        metrics["recommendations"].append("Améliorer couverture documentation")
        
    return metrics

def main():
    parser = argparse.ArgumentParser(description="Calculateur métriques documentation")
    parser.add_argument("--faits-documentation", required=True)
    args = parser.parse_args()
    
    try:
        with open(args.faits_documentation, 'r') as f:
            facts_data = json.load(f)
            
        metrics = calculate_documentation_metrics(facts_data)
        
        with open("metriques-documentation.json", 'w') as f:
            json.dump(metrics, f, indent=2)
            
        print(f"Métriques calculées - Couverture: {metrics['coverage_ratio']*100}%")
        
    except Exception as e:
        print(f"Erreur: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
