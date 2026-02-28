import os
import subprocess
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

ACTIVE_ROOT = os.environ.get('ACTIVE_ROOT', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEPLOY_DIR = os.path.join(ACTIVE_ROOT, 'vault', 'amplification')
PROJECT_NAME = "fajr-today" # Default project name for Cloudflare Pages

def deploy_to_cloudflare():
    print("🚀 Initiating Live Deployment to Cloudflare Pages...")
    
    # 1. Verify DEPLOY_DIR exists
    if not os.path.exists(DEPLOY_DIR):
        print(f"❌ Error: Deployment directory does not exist: {DEPLOY_DIR}")
        return False
    
    # 2. Check for required environment variables (for non-interactive CI/CD)
    # Note: If running locally, npx wrangler might trigger a browser login if tokens aren't found.
    account_id = os.environ.get('CLOUDFLARE_ACCOUNT_ID')
    api_token = os.environ.get('CLOUDFLARE_API_TOKEN')
    
    if not account_id or not api_token:
        print("⚠️ Warning: CLOUDFLARE_ACCOUNT_ID or CLOUDFLARE_API_TOKEN not found in environment.")
        print("   Wrangler may prompt for manual login.")

    # 3. Construct the wrangler command
    # We use 'npx wrangler pages deploy' for direct directory upload
    command = [
        "npx", "wrangler", "pages", "deploy",
        DEPLOY_DIR,
        f"--project-name={PROJECT_NAME}"
    ]
    
    # If we have an account ID, we specify it to avoid ambiguity
    if account_id:
        command.append(f"--account-id={account_id}")

    try:
        print(f"📡 Executing: {' '.join(command)}")
        # We run this with shell=True on Windows often to ensure npx is found in path correctly
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8')
        
        for line in process.stdout:
            print(line, end='')
            
        process.wait()
        
        if process.returncode == 0:
            print("✅ Deployment Successful!")
            return True
        else:
            print(f"❌ Deployment failed with exit code: {process.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ An error occurred during deployment: {e}")
        return False

if __name__ == "__main__":
    deploy_to_cloudflare()
