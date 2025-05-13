import os
import hashlib
import shutil
from pathlib import Path
from collections import defaultdict
from typing import Dict, List

# --- Pure function: Get hash of a file ---
def get_file_hash(filepath: Path, chunk_size: int = 8192) -> str:
    hasher = hashlib.sha256()
    with filepath.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

# --- Pure function: Map files to hashes ---
def hash_files_in_folder(folder: Path) -> Dict[str, List[Path]]:
    return (
        lambda files: defaultdict(list,
            {hash_: paths for hash_, paths in group_by_hash(files).items() if len(paths) > 1})
    )(list(folder.glob("*.csv")))

def group_by_hash(files: List[Path]) -> Dict[str, List[Path]]:
    return {
        h: list(g) for h, g in
        __import__('itertools').groupby(
            sorted(files, key=get_file_hash),
            key=get_file_hash
        )
    }

# --- Effectful function: Move one copy of each repeated file ---
def move_one_of_repeated(repeated_files: Dict[str, List[Path]], destination: Path) -> None:
    destination.mkdir(exist_ok=True)
    list(map(lambda paths: shutil.move(str(paths[1]), destination / paths[1].name), repeated_files.values()))

# --- Main execution ---
def main():
    source_folder = Path("CSV")
    target_folder = Path("REPEATED_csv")
    repeated = hash_files_in_folder(source_folder)
    move_one_of_repeated(repeated, target_folder)
    print(f"Moved {len(repeated)} repeated files to '{target_folder}'")

if __name__ == "__main__":
    main()
