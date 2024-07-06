from functions.fetcher import fetch_repositories_with_stars
from functions.generator import generate_html_page

def main():
    repositories = fetch_repositories_with_stars(min_stars=1)
    generate_html_page(repositories)

if __name__ == '__main__':
    main()
