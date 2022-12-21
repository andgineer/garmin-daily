"""
Create md-files from https://www.goodreads.com/ CSV export
"""
import pandas as pd
import os.path
import markdownify


def clean_filename(s: str, not_allowed: str = " %:/,.\\[]<>*?"):
    return ''.join([" " if ch in not_allowed else ch for ch in s])


def load_reviews(goodreads_export_csv_name: str) -> pd.DataFrame:
    df = pd.read_csv(goodreads_export_csv_name)
    return df


def dump_md(df: pd.DataFrame, folder: str) -> None:
    for index, book in df.iterrows():
        title = book["Title"]
        author = book["Author"]
        id_ = book["Book Id"]
        rating = book["My Rating"]
        stars = ("@" * rating).ljust(6, " ")
        review = book["My Review"]
        if isinstance(review, str):
            review = markdownify.markdownify(book["My Review"])
        else:
            review = ""
        file_name = f"{stars}{clean_filename(author)} - {clean_filename(title)}.md"
        book_url = f"https://www.goodreads.com/book/show/{id_}"
        if not isinstance(book["Bookshelves"], str):
            tags = []
        else:
            tags = [f"#book/{shelf.strip()}" for shelf in book["Bookshelves"].split(",")]
        with open(os.path.join(folder, f"{clean_filename(author)}.md"), "w") as f:
            f.write(author)
        with open(os.path.join(folder, file_name), "w") as f:
            f.write(f"""
[[{clean_filename(author)}]] [{title}]({book_url})
ISBN{book["ISBN"]} (ISBN13{book["ISBN13"]})

{review}

{" ".join(tags)}
""")


if __name__ == "__main__":
    df = load_reviews("~/Downloads/goodreads_library_export (1).csv")
    dump_md(df, "/Users/sorokan6/Library/CloudStorage/OneDrive-EPAM/Documents/Obsidian/anso-mobile/anso/books/goodreads")
