import gitlab
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_gitlab_client():
    try:
        # Get token from environment variable
        gitlab_url = os.getenv('GITLAB_URL')
        gitlab_token = os.getenv('GITLAB_TOKEN')
        
        if not all([gitlab_url, gitlab_token]):
            raise ValueError("GitLab credentials not found in environment variables")
        
        return gitlab.Gitlab(gitlab_url, private_token=gitlab_token)
    except Exception as e:
        print(f"Error in get_gitlab_client: {str(e)}")
        raise

def search_gitlab_projects(query_text):
    try:
        gl = get_gitlab_client()
        # Search projects
        projects = gl.projects.list(search=query_text, order_by='stars_count', sort='desc')
        
        results = []
        for project in projects[:10]:  # Get top 10 results
            results.append({
                'name': project.name,
                'path': project.path_with_namespace,
                'description': project.description,
                'stars': project.star_count,
                'url': project.web_url
            })
        return results
    except Exception as e:
        print(f"Error in search_gitlab_projects: {str(e)}")
        raise 