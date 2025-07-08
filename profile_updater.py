import requests
import os

# --- Configuration ---
# Global settings for the script.
# These variables define the target user and the markers for content injection.

GITHUB_USERNAME = "theArchitectEngineer101"
API_URL = f"https://api.github.com/users/{GITHUB_USERNAME}/repos"

# These HTML comments act as markers in the README.md file.
# The script will find these markers and replace everything between them.
START_MARKER = "<!--START_REPOS_LIST-->"
END_MARKER = "<!--END_REPOS_LIST-->"


def fetch_repos():
    """
    Fetches the list of public repositories for the specified user from the GitHub API.
    Returns a list of repository data as JSON, or None if the request fails.
    """
    print(f"Fetching repositories for user: {GITHUB_USERNAME}...")
    response = requests.get(API_URL)
    
    if response.status_code == 200:
        print("✅ Repositories found successfully.")
        return response.json()
    else:
        print(f"❌ Error fetching repositories: {response.status_code}")
        return None


def format_repos_as_markdown(repos):
    """
    Takes a list of repository data and formats it into a Markdown bulleted list.
    It filters out the profile's own repository and sorts the list by the most recently updated.
    """
    if not repos:
        return "No projects found."
    
    # Exclude the special profile repository from the list to avoid self-listing.
    filtered_repos = [repo for repo in repos if repo['name'] != GITHUB_USERNAME]
    
    # Sort repositories by the 'updated_at' field to show the most active ones first.
    sorted_repos = sorted(filtered_repos, key=lambda x: x['updated_at'], reverse=True)

    markdown_list = []
    for repo in sorted_repos:
        repo_name = repo['name']
        repo_url = repo['html_url']
        # Use the repository's description if available, otherwise provide a default text.
        description = repo.get('description') or "No description provided."
        markdown_list.append(f"- **[{repo_name}]({repo_url})**: {description}")
    
    # Join all list items into a single string with newlines.
    return "\n".join(markdown_list)


def update_readme(repo_list_md):
    """
    Reads the README.md file, finds the start and end markers, and injects
    the formatted list of repositories between them.
    """
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            readme_content = f.read()

        # Find the exact positions of our markers in the file content.
        start_index = readme_content.find(START_MARKER)
        end_index = readme_content.find(END_MARKER)

        if start_index == -1 or end_index == -1:
            print("❌ Markers not found in README.md. Please add them to the file.")
            return

        # Reconstruct the file content with the new list.
        # It keeps the content before the start marker and after the end marker.
        new_readme = (
            readme_content[:start_index + len(START_MARKER)] +
            "\n\n" +
            repo_list_md +
            "\n\n" +
            readme_content[end_index:]
        )

        # Write the newly constructed content back to the README.md file.
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(new_readme)
        
        print("✅ README.md updated successfully!")

    except FileNotFoundError:
        print("❌ README.md file not found in the current directory.")


# --- Main Execution ---
# This block runs only when the script is executed directly (not when imported).
if __name__ == "__main__":
    # 1. Fetch the repository data.
    repos = fetch_repos()
    
    # 2. If fetching was successful, format the data and update the README.
    if repos:
        repo_list_markdown = format_repos_as_markdown(repos)
        update_readme(repo_list_markdown)