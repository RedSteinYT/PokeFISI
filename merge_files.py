import os

with open('src/game_logic.py', 'r', encoding='utf-8') as f:
    content = f.read()
    
with open('src/game_logic_append.py', 'r', encoding='utf-8') as f:
    append = f.read()
    
with open('src/game_logic.py', 'w', encoding='utf-8') as f:
    f.write(content + '\n' + append)
    
os.remove('src/game_logic_append.py')
os.remove('merge_files.py')
print("Files merged successfully")
