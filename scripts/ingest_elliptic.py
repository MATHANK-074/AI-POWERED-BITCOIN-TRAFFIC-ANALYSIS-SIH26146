import sys
import argparse
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.ingestion.elliptic import EllipticDatasetParser
from app.database.duckdb_manager import DuckDBManager

def main():
    parser = argparse.ArgumentParser(description="Ingest Elliptic Bitcoin Dataset into DuckDB")
    parser.add_argument("--dir", type=str, default="data/external/elliptic", help="Path to directory containing Elliptic CSV files")
    args = parser.parse_args()

    dir_path = Path(args.dir)
    classes_file = dir_path / "elliptic_txs_classes.csv"
    edgelist_file = dir_path / "elliptic_txs_edgelist.csv"
    features_file = dir_path / "elliptic_txs_features.csv"

    print(f"Checking for Elliptic dataset in: {dir_path}")
    if not classes_file.exists():
        print(f"Error: Could not find {classes_file}")
        sys.exit(1)

    elliptic_parser = EllipticDatasetParser()
    print("Ingesting Elliptic dataset...")
    valid_df, edges_df, stats = elliptic_parser.parse_elliptic_dataset(
        str(classes_file), str(edgelist_file), str(features_file)
    )

    db = DuckDBManager()
    db.save_transactions(valid_df)

    print(f"Successfully ingested Elliptic dataset:")
    print(f" - Records Processed: {stats['records_processed']:,}")
    print(f" - Illicit Transactions: {stats.get('elliptic_illicit_count', 0):,}")
    print(f" - Graph Edges: {stats.get('elliptic_edges_count', 0):,}")
    print(f" - Processing Time: {stats['processing_time_sec']} seconds")

if __name__ == "__main__":
    main()
