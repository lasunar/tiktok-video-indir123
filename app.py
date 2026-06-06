from flask import Flask, render_template, request, jsonify, Response, stream_with_context
import requests

app = Flask(__name__)

def get_tiktok_video(url):
    try:
        api_url = f"https://www.tikwm.com/api/?url={url}"
        response = requests.get(api_url).json()
        
        if response.get("code") == 0:
            video_data = response.get("data", {})
            return {
                "success": True,
                "title": video_data.get("title", "TikTok Videosu"),
                "download_url": video_data.get("play")
            }
        else:
            return {"success": False, "message": "Video bulunamadı. Linki kontrol edin."}
    except Exception as e:
        return {"success": False, "message": "Bir hata oluştu: " + str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch-video', methods=['POST'])
def fetch_video():
    data = request.get_json()
    tiktok_url = data.get('url')
    
    if not tiktok_url:
        return jsonify({"success": False, "message": "Link boş olamaz!"})
        
    result = get_tiktok_video(tiktok_url)
    return jsonify(result)

# RENDER'I ÇÖKERTMEYEN, DİREKT İNDİRTEN YENİ KÖPRÜ (STREAM)
@app.route('/proxy-download')
def proxy_download():
    video_url = request.args.get('url')
    if not video_url:
        return "Link bulunamadı", 400
        
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        req = requests.get(video_url, headers=headers, stream=True)
        
        # Videoyu sunucuda bekletmeden direkt telefona akıtıyoruz
        def generate():
            for chunk in req.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk

        response = Response(stream_with_context(generate()), content_type='video/mp4')
        response.headers['Content-Disposition'] = 'attachment; filename=tiktok_video.mp4'
        return response
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
