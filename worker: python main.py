{
  "$schema": "https://schema.up.railway.app/railway.schema.json",
  "build": {
    "builder": "nixpacks",
    "buildCommand": "pip install -r requirements.txt"
  },
  "deploy": {
    "startCommand": "python main.py",
    "restartPolicyType": "ALWAYS",
    "restartPolicyMaxRetries": 100
  }
}
