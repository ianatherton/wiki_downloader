import pickle
import os

def inspect_progress():
    progress_file = "/home/sparky/python_projs/wiki_downloader/data/progress.pkl"

    if not os.path.exists(progress_file):
        print("Progress file not found.")
        return

    with open(progress_file, 'rb') as file:
        progress = pickle.load(file)

    visited_pages, pages_to_visit, total_pages = progress

    print(f"Total pages downloaded: {len(visited_pages)}")
    print(f"Total links discovered: {len(visited_pages) + len(pages_to_visit)}")
    print(f"Pages remaining to download: {len(pages_to_visit)}")

if __name__ == "__main__":
    inspect_progress()