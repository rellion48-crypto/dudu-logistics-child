from pathlib import Path
import shutil
p=Path(__file__).parent
shutil.copy2(p/"baseline"/"settings.py",p/"settings.py")
print("COMPLETE RAG LAB RESET")
