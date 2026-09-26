import pandas as pd
from typing import Dict, Any, Tuple
from app.explainability.lead_generator import LeadGenerator

class PriorityScorer:
    """
    Priority Scoring adapter forwarding to LeadGenerator.
    """
    def __init__(self):
        self.generator = LeadGenerator()

    def generate_leads(
        self,
        features_df: pd.DataFrame,
        anomalies_df: pd.DataFrame,
        correlated_df: pd.DataFrame,
        transactions_df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        return self.generator.generate_leads(features_df, anomalies_df, correlated_df, transactions_df)
