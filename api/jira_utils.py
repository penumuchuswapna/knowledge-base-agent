from jira import JIRA
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_jira_client():
    try:
        # Get credentials from environment variables
        jira_url = os.getenv('JIRA_URL')
        jira_email = os.getenv('JIRA_EMAIL')
        jira_token = os.getenv('JIRA_TOKEN')

        if not all([jira_url, jira_email, jira_token]):
            raise ValueError("Jira credentials not found in environment variables")

        return JIRA(
            server=jira_url,
            basic_auth=(jira_email, jira_token)
        )
    except Exception as e:
        print(f"Error in get_jira_client: {str(e)}")
        raise

def search_jira_issues(query_text):
    try:
        jira = get_jira_client()
        # Search for issues containing the query text in summary or description
        jql = f'text ~ "{query_text}"'
        issues = jira.search_issues(jql, maxResults=10)
        
        results = []
        for issue in issues:
            results.append({
                'key': issue.key,
                'summary': issue.fields.summary,
                'status': issue.fields.status.name,
                'url': f"{jira._options['server']}/browse/{issue.key}"
            })
        return results
    except Exception as e:
        print(f"Error in search_jira_issues: {str(e)}")
        raise 