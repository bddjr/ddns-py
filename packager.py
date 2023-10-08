exec(open('ddns.py', 'r', encoding='utf-8').readline())

import shutil, os
shutil.rmtree('releases')  
os.mkdir('releases')

files = {
    "no-readme": [
        "ddns.py",
        "ddns.py.bat"
    ],
    "default": [
        "README.md",
        "readmepic"
    ]
}

os.system('bandizip c releases/ddns-py-release-{}-no-readme.zip {}'.format(version, ' '.join(files['no-readme'])))
os.system('bandizip c releases/ddns-py-release-{}.zip {} {}'.format(version, ' '.join(files['no-readme']), ' '.join(files['default'])))
