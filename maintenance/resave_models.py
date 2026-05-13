import os
import logging
import argparse
import shutil
import traceback
import flair
from flair.nn import Classifier


def main():
    # Set up argparse
    parser = argparse.ArgumentParser(description="Migrate Flair models.")
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="Overwrite the original models directly WITHOUT keeping a .old backup.",
    )
    args = parser.parse_args()

    # Set up flair logging to show what's happening during conversion
    logging.basicConfig(level=logging.INFO)

    models = {"ner-bio": "./models/ner-bio.pt", "ner-det": "./models/ner-det.pt"}

    current_version = flair.__version__
    print(f"--- Flair Model Migration (Legacy -> {current_version}) ---")
    print(f"Detecting Flair version from environment: {current_version}")

    for name, path in models.items():
        if not os.path.exists(path):
            print(f"[!] Model not found at {path}, skipping.")
            continue

        new_path = f"{path}.new"
        print(f"\n[*] Processing {name}...")
        print(f"    Source: {path}")

        try:
            # Load the model (Flair will perform internal conversion if needed)
            print(
                "    Loading and converting (this will generate some console noise)..."
            )
            tagger = Classifier.load(path)

            # Save the migrated model temporarily
            print("    Saving migrated version...")
            tagger.save(new_path)

            # Replace logic
            if args.in_place:
                print("    Replacing original model in place (no backup)...")
                # Overwrite directly by removing the old one first
                os.remove(path)
                shutil.move(new_path, path)
                print(f"    [OK] Successfully migrated and overwritten {name}.")
            else:
                old_path = f"{path}.old"
                print(f"    Moving original to {old_path} and replacing in place...")
                shutil.move(path, old_path)
                shutil.move(new_path, path)
                print(f"    [OK] Successfully migrated {name} (backup saved to .old).")

        except Exception as e:
            print(f"    [ERROR] Failed to migrate {name}: {e}")
            traceback.print_exc()

    print("\n--- Migration Complete ---")


if __name__ == "__main__":
    main()
