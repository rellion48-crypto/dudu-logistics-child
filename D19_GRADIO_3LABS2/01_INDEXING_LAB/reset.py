from pathlib import Path
import shutil
p=Path(__file__).parent
shutil.copy2(p/"baseline"/"faq.json",p/"faq.json")
print("INDEXING LAB RESET")
