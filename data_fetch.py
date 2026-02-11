import scrapetube
import random
import time
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound, TranscriptsDisabled

yt_api = YouTubeTranscriptApi()

def get_video_ids(playlist_id_or_url):
    print(f"fetching Video Ids for {playlist_id_or_url} : \n")

    if "list=" in playlist_id_or_url:
        playlist_id = playlist_id_or_url.split('list=')[1].split('&')[0]
    else:
        playlist_id = playlist_id_or_url
    
    try:
        videos = scrapetube.get_playlist(playlist_id)
        video_id = [video['videoId'] for video in videos]
        print(f"fetched {len(video_id)} videos from playlist \n")
        return video_id
    except Exception as e:
        print(f"Error fetching playlist : {e}")
        return []


def fetch_transcript(video_id: str):
    sleep_time = random.uniform(2.0, 5.0)
    print(f"Sleeping for {sleep_time:.2f}s before fetching {video_id}...")
    time.sleep(sleep_time)

    try:
        transcript_list = yt_api.list(video_id)
        
        try:
            transcript = transcript_list.find_transcript(['en', 'hi'])
        except NoTranscriptFound:
            print(f"  Strict match failed for {video_id}. Attempting to fetch any available language...")
            transcript = next(iter(transcript_list))
        
        if not transcript.language_code.startswith('en'):
            print(f"  Translating {video_id} (from {transcript.language_code}) to English...")
            transcript = transcript.translate('en')

        raw_transcript = transcript.fetch()
        
        # FIX: Create a NEW dictionary list because raw_transcript is read-only
        transcript_data = []
        for seg in raw_transcript:
            if hasattr(seg, 'text'):
                text = seg.text
                start = seg.start
                duration = getattr(seg, 'duration', 0.0)
            else:
                # Fallback to dictionary access
                text = seg['text']
                start = seg['start']
                duration = seg.get('duration', 0.0)

            clean_seg = {
                'text': text,
                'start': start,
                'duration': duration,
                'video_id': video_id
            }
            transcript_data.append(clean_seg)
            
        return transcript_data

    except (NoTranscriptFound, TranscriptsDisabled):
        print(f"Skipped Video : {video_id} (Truly no transcript available or Age Restricted)")
        return None
    except Exception as e:
        print(f"Error processing {video_id}: {e}")
        return None