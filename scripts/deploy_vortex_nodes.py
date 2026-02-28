import os
import subprocess
import shutil
import time

# ==========================================
# NODAL DEPLOYMENT (VORTEX OUTPUT)
# ==========================================
# This script initializes the isolated `public_nodes` folder
# as a completely severable Git repository and force-pushes it 
# to a generic, disposable GitHub Pages outpost.
# ==========================================

ACTIVE_ROOT = os.environ.get('ACTIVE_ROOT', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NODE_DIR = os.path.join(ACTIVE_ROOT, 'public_nodes')

# The exact disposable repository URL (can be changed to any burner account repo)
DISPOSABLE_REMOTE_URL = "https://github.com/dours-d/palestine-resilience-network.git"

def run_cmd(cmd, cwd=NODE_DIR, silent=False):
    try:
        result = subprocess.run(cmd, cwd=cwd, shell=True, check=True, text=True, capture_output=True)
        if not silent:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        if not silent:
            print(f"ERROR executing '{cmd}':\n{e.stderr}")
        return False

def deploy_nodes():
    print("🌀 Initiating Nodal Deployment to Disposable Outpost...")
    
    if not os.path.exists(NODE_DIR):
        print("Error: /public_nodes directory does not exist. Run generate_seo_nodes.py first.")
        return

    # Check if we need to initialize a completely separate git repo for just this folder
    git_dir = os.path.join(NODE_DIR, '.git')
    if not os.path.exists(git_dir):
        print("Initializing isolated node repository...")
        run_cmd("git init")
        run_cmd(f"git remote add origin {DISPOSABLE_REMOTE_URL}")
    
    # We always use the 'main' branch for the outpost
    run_cmd("git checkout -b main", silent=True) # Ignore error if branch exists
    run_cmd("git checkout main", silent=True)
    
    print("Committing fresh nodes...")
    run_cmd("git add -A")
    
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    run_cmd(f'git commit -m "Vortex Propagation: {timestamp}"')
    
    print(f"Force-pushing to {DISPOSABLE_REMOTE_URL} ...")
    success = run_cmd("git push -f origin main")
    
    if success:
        print("\n✅ DEPLOYMENT COMPLETE.")
        print("The nodes have been successfully deployed to the outpost.")
        print("They are now severable from the source system.")
    else:
        print("\n❌ DEPLOYMENT FAILED. Check permissions or repository existence.")

if __name__ == "__main__":
    deploy_nodes()
