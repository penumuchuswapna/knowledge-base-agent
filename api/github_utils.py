from github import Github
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_github_client():
    try:
        # Get token from environment variable
        github_token = os.getenv('GITHUB_TOKEN')
        if not github_token:
            raise ValueError("GitHub token not found in environment variables")
        
        return Github(github_token)
    except Exception as e:
        print(f"Error in get_github_client: {str(e)}")
        raise

def search_github_repos(query_text):
    try:
        github = get_github_client()
        # Search repositories
        repos = github.search_repositories(query=query_text, sort="stars", order="desc")
        
        results = []
        for repo in repos[:10]:  # Get top 10 results
            results.append({
                'name': repo.name,
                'full_name': repo.full_name,
                'description': repo.description,
                'stars': repo.stargazers_count,
                'url': repo.html_url
            })
        return results
    except Exception as e:
        print(f"Error in search_github_repos: {str(e)}")
        raise 