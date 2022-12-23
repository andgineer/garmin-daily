"""Create md-files from https://www.goodreads.com/ CSV export."""
import os.path

import markdownify
import pandas as pd


def clean_filename(file_name: str, not_allowed: str = ' %:/,.\\[]<>*?"|#') -> str:
    """Replace with spaces chars unsafe for file name."""
    return "".join([" " if ch in not_allowed else ch for ch in file_name]).strip()


def load_reviews(goodreads_export_csv_name: str) -> pd.DataFrame:
    """Load goodreads books infor from CSV export."""
    return pd.read_csv(goodreads_export_csv_name)


def dump_md(books_df: pd.DataFrame, folder: str) -> None:  # pylint: disable=too-many-locals
    """Save books and authors as md-files."""
    for _, book in books_df.iterrows():
        title = book["Title"]
        author = book["Author"]
        id_ = book["Book Id"]
        rating = book["My Rating"]
        if rating == 0:
            stars = ""
        else:
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
        tags.append("#book/book")
        if rating > 0:
            tags.append(f"#book/rating{rating}")
        with open(
            os.path.join(folder, "authors", f"{clean_filename(author)}.md"), "w", encoding="utf8"
        ) as md_file:
            author_article = f"{author}\n\n#book/author"
            md_file.write(author_article)
        if review == "" and rating == 0:
            subfolder = "toread"
        else:
            subfolder = "reviews"
        with open(os.path.join(folder, subfolder, file_name), "w", encoding="utf8") as md_file:
            book_article = f"""
[[{clean_filename(author)}]]: [{title}]({book_url})
ISBN{book["ISBN"]} (ISBN13{book["ISBN13"]})

{review}

{" ".join(tags)}
"""
            md_file.write(book_article)


if __name__ == "__main__":
    books = load_reviews("~/Downloads/goodreads_library_export (1).csv")
    dump_md(
        books,
        (
            "/Users/sorokan6/Library/CloudStorage/OneDrive-EPAM/"
            "Documents/Obsidian/anso-mobile/anso/books/"
        ),
    )
