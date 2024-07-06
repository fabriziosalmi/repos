from typing import List, Dict
from functions.fetcher import fetch_repositories_with_stars
from functions.generator import generate_html_page


def main() -> None:
    """
    Main function to fetch repositories with a minimum number of stars
    and generate an HTML page based on the fetched repositories.
    """
    try:
        repositories = fetch_repositories_with_stars(min_stars=1)
        if not repositories:
            raise ValueError("No repositories found with the specified criteria.")
        generate_html_page(repositories)
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == '__main__':
    main()
