def run_planning_pipeline():
    """
    This will call your existing FSD AI Agent pipeline
    using the SAME Python interpreter as the current venv.
    """

    print("🚀 Running full planning pipeline...")

    import subprocess
    import sys

    script_path = r"C:\Users\shash\OneDrive\Desktop\FSD AI AGENT\run_agent.py"

    result = subprocess.run(
        [sys.executable, script_path],
        capture_output=True,
        text=True,
        cwd=r"C:\Users\shash\OneDrive\Desktop\FSD AI AGENT"   # 👈 ADD THIS LINE
    )

    return {
        "status": "success" if result.returncode == 0 else "failed",
        "output": result.stdout,
        "error": result.stderr
    }