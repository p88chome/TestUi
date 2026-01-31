"""
Video/Audio Transcription Skill
將影片或音訊檔案轉換為逐字稿
支援 Whisper 和 Google Speech Recognition
"""

import os
import tempfile
from pathlib import Path
from datetime import timedelta


def extract_audio_from_video(video_path: str, audio_path: str) -> bool:
    """從影片中提取音訊"""
    try:
        from moviepy.video.io.VideoFileClip import VideoFileClip
        
        video = VideoFileClip(video_path)
        audio = video.audio
        audio.write_audiofile(audio_path, logger=None)
        
        audio.close()
        video.close()
        
        return True
    except Exception as e:
        print(f"音訊提取失敗: {str(e)}")
        return False


def transcribe_with_whisper(audio_path: str, model_size: str = "base", language: str = "zh") -> dict:
    """使用 OpenAI Whisper 進行語音識別"""
    try:
        import whisper
        
        model = whisper.load_model(model_size)
        result = model.transcribe(
            audio_path,
            language=language,
            verbose=False
        )
        
        return {
            'success': True,
            'text': result['text'],
            'segments': result.get('segments', []),
            'language': result.get('language', language),
            'error': None
        }
    except Exception as e:
        return {
            'success': False,
            'text': '',
            'segments': [],
            'language': language,
            'error': str(e)
        }


def transcribe_with_google(audio_path: str, language: str = "zh-TW") -> dict:
    """使用 Google Speech Recognition"""
    try:
        import speech_recognition as sr
        from pydub import AudioSegment
        
        r = sr.Recognizer()
        audio = AudioSegment.from_wav(audio_path)
        
        # 分段處理 (Google 有時間限制)
        chunk_length_ms = 60000  # 60秒
        chunks = []
        
        for i in range(0, len(audio), chunk_length_ms):
            chunk = audio[i:i + chunk_length_ms]
            chunk_path = f"temp_chunk_{i//chunk_length_ms}.wav"
            chunk.export(chunk_path, format="wav")
            
            try:
                with sr.AudioFile(chunk_path) as source:
                    audio_data = r.record(source)
                    text = r.recognize_google(audio_data, language=language)
                    chunks.append(text)
            except sr.UnknownValueError:
                chunks.append("[無法識別]")
            except sr.RequestError as e:
                chunks.append(f"[錯誤: {e}]")
            finally:
                if os.path.exists(chunk_path):
                    os.remove(chunk_path)
        
        full_text = " ".join(chunks)
        
        return {
            'success': True,
            'text': full_text,
            'segments': [],
            'language': language,
            'error': None
        }
    except Exception as e:
        return {
            'success': False,
            'text': '',
            'segments': [],
            'language': language,
            'error': str(e)
        }


def run(file_path: str, method: str = "whisper", model_size: str = "base", 
        language: str = "zh", include_timestamps: bool = True, **kwargs) -> dict:
    """
    主要執行函數
    
    Args:
        file_path: 音訊或影片檔案路徑
        method: 識別方法 (whisper 或 google)
        model_size: Whisper 模型大小
        language: 語言代碼
        include_timestamps: 是否包含時間戳
    
    Returns:
        dict: 包含轉錄結果的字典
    """
    if not os.path.exists(file_path):
        return {
            'success': False,
            'text': '',
            'segments': [],
            'language': language,
            'error': f'檔案不存在: {file_path}'
        }
    
    # 判斷是影片還是音訊
    file_ext = Path(file_path).suffix.lower()
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.webm']
    audio_extensions = ['.mp3', '.wav', '.m4a', '.aac', '.flac', '.ogg']
    
    # 準備音訊檔案
    if file_ext in video_extensions:
        # 從影片提取音訊
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
            audio_path = temp_audio.name
        
        if not extract_audio_from_video(file_path, audio_path):
            return {
                'success': False,
                'text': '',
                'segments': [],
                'language': language,
                'error': '無法從影片提取音訊'
            }
        cleanup_audio = True
    elif file_ext in audio_extensions:
        audio_path = file_path
        cleanup_audio = False
    else:
        return {
            'success': False,
            'text': '',
            'segments': [],
            'language': language,
            'error': f'不支援的檔案格式: {file_ext}'
        }
    
    try:
        # 執行語音識別
        if method.lower() == "whisper":
            result = transcribe_with_whisper(audio_path, model_size, language)
        elif method.lower() == "google":
            result = transcribe_with_google(audio_path, language)
        else:
            result = {
                'success': False,
                'text': '',
                'segments': [],
                'language': language,
                'error': f'不支援的識別方法: {method}'
            }
        
        return result
    
    finally:
        # 清理暫存音訊檔案
        if cleanup_audio and os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except:
                pass


if __name__ == "__main__":
    # 測試用
    import sys
    if len(sys.argv) > 1:
        result = run(sys.argv[1])
        print(f"成功: {result['success']}")
        print(f"文字長度: {len(result['text'])}")
        print(f"預覽: {result['text'][:200]}")
