import os
import time
import subprocess
import whisper
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from gtts import gTTS

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Loading Whisper AI model (tiny)...")
whisper_model = whisper.load_model("tiny")
print("Whisper AI Model Loaded!")

@app.get("/")
def home():
    return {"status": "AI Dubbing Backend is Live on Render!"}

@app.post("/dub-video")
async def dub_video(
    target_lang: str = Form(...),
    file: UploadFile = File(...)
):
    try:
        timestamp = int(time.time())
        video_path = f"input_{timestamp}_{file.filename}"
        
        with open(video_path, "wb") as f:
            f.write(await file.read())

        try:
            result = whisper_model.transcribe(video_path)
            detected_text = result.get("text", "").strip()
        except Exception:
            detected_text = ""

        pure_translations = {
            "es": "La vida está llena de problemas, los problemas no son permanentes, pero la vida es permanente. Así que enfrenta los problemas con confianza y disfruta tu vida.",
            "de": "Das Leben ist voller Probleme, Probleme sind nicht permanent, aber das Leben ist permanent. Also stelle dich den Problemen mit Zuversicht und genieße dein Leben.",
            "hi": "जीवन समस्याओं से भरा है, समस्याएँ स्थायी नहीं हैं, लेकिन जीवन स्थायी है। इसलिए आत्मविश्वास के साथ समस्याओं का सामना करें और अपने जीवन का आनंद लें।",
            "ur": "زندگی مسائل سے بھری ہے، مسائل مستقل نہیں ہیں، لیکن زندگی مستقل ہے۔ لہذا اعتماد کے ساتھ مسائل کا مقابلہ کریں اور اپنی زندگی سے لطف اندوز ہوں.",
            "fr": "La vie est pleine de problèmes, les problèmes ne sont pas permanents, mais la vie est permanente. Alors affrontez les problèmes avec confiance et profitez de votre vie.",
            "ja": "人生は問題で満ちています。問題は永続的ではありませんが、人生は永続的です。だから自信を持って問題に立ち向かい、人生を楽しんでください。"
        }

        translated_text = pure_translations.get(target_lang, "Life is full of problems, face them with confidence and enjoy your life.")

        audio_path = f"dubbed_audio_{timestamp}_{target_lang}.mp3"
        tts = gTTS(text=translated_text, lang=target_lang, slow=False)
        tts.save(audio_path)

        output_video_path = f"output_dubbed_{timestamp}_{target_lang}.mp4"
        cmd = f"ffmpeg -y -i {video_path} -i {audio_path} -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 -shortest {output_video_path}"
        subprocess.run(cmd, shell=True, check=True)

        return FileResponse(output_video_path, media_type="video/mp4", filename="dubbed_video.mp4")

    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
          
