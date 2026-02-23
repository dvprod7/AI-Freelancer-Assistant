import subprocess

print("🚀 Freelancer Assistant Starting...\n")

print("STEP 1 — Finding leads")
subprocess.run(["python", "tools/find_leads.py"])

print("\nSTEP 2 — Running AI analysis")
subprocess.run(["python", "agent/analyzer.py"])

print("\n✅ Workflow complete!")