from flask import Flask, render_template, send_file
from pathlib import Path
import random

app = Flask('__name__')

@app.route('/')
def home():
    path = Path('static/')
    random_media = random.choice(list(path.rglob('*')))
    is_video = "mp4" in str(random_media)
    return render_template('download.html', mediapath=random_media, is_video=is_video)

@app.route('/download')
def download():
    return send_file('PepperInstaller/PepperInstaller.exe', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)