#!/usr/bin/env python3
"""
Automated GitHub deployment script for AI Support Assistant
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, check=True):
    """Run a shell command and return the result."""
    print(f"🔧 Running: {command}")
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return None

def check_git_installed():
    """Check if git is installed."""
    result = run_command("git --version", check=False)
    return result is not None and result.returncode == 0

def check_gh_cli_installed():
    """Check if GitHub CLI is installed."""
    result = run_command("gh --version", check=False)
    return result is not None and result.returncode == 0

def initialize_git_repo():
    """Initialize git repository if not already done."""
    if not Path(".git").exists():
        print("📁 Initializing git repository...")
        run_command("git init")
        run_command("git add .")
        run_command('git commit -m "Initial commit: AI Support Assistant with Endee vector database"')
    else:
        print("✅ Git repository already initialized")

def create_github_repo(repo_name="ai-support-assistant"):
    """Create GitHub repository using GitHub CLI."""
    if not check_gh_cli_installed():
        print("❌ GitHub CLI not found. Please install it:")
        print("Windows: winget install GitHub.cli")
        print("Mac: brew install gh")
        print("Linux: https://cli.github.com/")
        return False
    
    print("🔐 Checking GitHub authentication...")
    auth_result = run_command("gh auth status", check=False)
    
    if auth_result is None or auth_result.returncode != 0:
        print("🔑 Please login to GitHub:")
        run_command("gh auth login")
    
    print(f"🚀 Creating GitHub repository: {repo_name}")
    create_result = run_command(
        f'gh repo create {repo_name} --public --description "AI-powered Support Assistant using Endee vector database for semantic search"',
        check=False
    )
    
    if create_result and create_result.returncode == 0:
        print("✅ GitHub repository created successfully!")
        return True
    else:
        print("⚠️  Repository might already exist or there was an error")
        return False

def setup_remote_and_push(username, repo_name="ai-support-assistant"):
    """Setup git remote and push to GitHub."""
    print("🔗 Setting up git remote...")
    
    # Remove existing origin if it exists
    run_command("git remote remove origin", check=False)
    
    # Add new origin
    remote_url = f"https://github.com/{username}/{repo_name}.git"
    run_command(f"git remote add origin {remote_url}")
    
    # Set main branch and push
    run_command("git branch -M main")
    
    print("📤 Pushing to GitHub...")
    push_result = run_command("git push -u origin main", check=False)
    
    if push_result and push_result.returncode == 0:
        print("✅ Code pushed to GitHub successfully!")
        print(f"🌐 Repository URL: https://github.com/{username}/{repo_name}")
        return True
    else:
        print("❌ Failed to push to GitHub")
        return False

def create_github_pages():
    """Create GitHub Pages branch."""
    print("📄 Creating GitHub Pages...")
    
    # Create gh-pages branch
    run_command("git checkout -b gh-pages")
    
    # Create simple index.html
    index_html = """<!DOCTYPE html>
<html>
<head>
    <title>AI Support Assistant - Demo</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .demo-link { background: #007bff; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 0; }
        .feature { background: #f8f9fa; padding: 15px; margin: 10px 0; border-left: 4px solid #007bff; }
        pre { background: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto; }
    </style>
</head>
<body>
    <h1>🤖 AI Support Assistant</h1>
    <p>Intelligent customer support system using Endee vector database for semantic search.</p>
    
    <div class="feature">
        <h3>🔍 Semantic Search</h3>
        <p>Uses vector embeddings to find similar support tickets based on meaning, not just keywords.</p>
    </div>
    
    <div class="feature">
        <h3>🗄️ Endee Vector Database</h3>
        <p>High-performance vector storage and similarity search with cosine distance.</p>
    </div>
    
    <div class="feature">
        <h3>💬 Conversational AI</h3>
        <p>Context-aware response generation with confidence scoring.</p>
    </div>
    
    <h2>🚀 Quick Start</h2>
    <pre><code>git clone https://github.com/yourusername/ai-support-assistant.git
cd ai-support-assistant
pip install -r requirements.txt
python demo_app.py</code></pre>
    
    <p>Then visit <strong>http://localhost:8000</strong> for the interactive demo.</p>
    
    <h2>📚 Documentation</h2>
    <ul>
        <li><a href="README.md">Complete README</a></li>
        <li><a href="SETUP.md">Setup Guide</a></li>
        <li><a href="GITHUB_HOSTING.md">GitHub Hosting Guide</a></li>
    </ul>
    
    <h2>🎯 Features Demonstrated</h2>
    <ul>
        <li>Semantic vector search using Endee</li>
        <li>Retrieval Augmented Generation (RAG)</li>
        <li>Intelligent response classification</li>
        <li>Modern web interface</li>
        <li>REST API endpoints</li>
        <li>Production-ready architecture</li>
    </ul>
    
    <p><strong>⭐ Star this repository if you find it useful!</strong></p>
</body>
</html>"""
    
    with open("index.html", "w") as f:
        f.write(index_html)
    
    run_command("git add index.html")
    run_command('git commit -m "Add GitHub Pages demo page"')
    run_command("git push origin gh-pages")
    
    # Switch back to main
    run_command("git checkout main")
    
    print("✅ GitHub Pages created! Enable it in repository settings.")

def main():
    """Main deployment function."""
    print("🚀 AI Support Assistant - GitHub Deployment Script")
    print("=" * 50)
    
    # Check prerequisites
    if not check_git_installed():
        print("❌ Git is not installed. Please install Git first.")
        sys.exit(1)
    
    # Get user input
    username = input("Enter your GitHub username: ").strip()
    if not username:
        print("❌ Username is required")
        sys.exit(1)
    
    repo_name = input("Enter repository name (default: ai-support-assistant): ").strip()
    if not repo_name:
        repo_name = "ai-support-assistant"
    
    # Initialize git repository
    initialize_git_repo()
    
    # Create GitHub repository
    create_github_repo(repo_name)
    
    # Setup remote and push
    if setup_remote_and_push(username, repo_name):
        print("\n🎉 Deployment successful!")
        print(f"📍 Repository: https://github.com/{username}/{repo_name}")
        
        # Ask about GitHub Pages
        create_pages = input("\nCreate GitHub Pages demo? (y/n): ").strip().lower()
        if create_pages in ['y', 'yes']:
            create_github_pages()
            print(f"📄 GitHub Pages will be available at: https://{username}.github.io/{repo_name}/")
            print("   (Enable it in repository Settings > Pages)")
        
        print("\n✅ Next steps:")
        print("1. Go to your repository settings to enable GitHub Pages")
        print("2. Add repository topics: ai, machine-learning, vector-database, semantic-search")
        print("3. Create a release tag: git tag v1.0.0 && git push origin v1.0.0")
        print("4. Consider deploying to Heroku, Railway, or Render for live demo")
        
    else:
        print("❌ Deployment failed. Please check the errors above.")

if __name__ == "__main__":
    main()