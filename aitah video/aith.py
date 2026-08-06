from gtts import gTTS
from moviepy.editor import TextClip, AudioFileClip, CompositeVideoClip
import os

# Step 1: AITA Post (Manually Copied or Scraped)
aita_text = """A few months ago, after many years of trying to conceive, my husband (32M) and I (33F) had a gorgeous, healthy baby boy. My husband and I are black, which is pertinent to this story.

We were over the moon, and family, friends, and coworkers had also been excited for us. Right after I delivered, my husband emailed a birth announcement with a photo of our son to everyone in his office.

Fast forward a couple of weeks, and my husband came home fuming after his first day back at work. One of his coworkers informed him that another guy in the office, a new young employee my husband barely knew, had been telling everyone willing to listen that my husband couldn't be our son's father because, "That baby is too light to be his and its hair is too long and straight. That's a white man's baby, or an Asian's."

This guy proceeded to tell everyone what a sucker my husband was and that his excitement over finally becoming a dad was blinding him to the reality that he had been cheated on and his wife impregnated by another man.

Side note for anyone who's still unaware in 2025: black babies in general are fairly pale as newborns, and their skin will darken over the first few weeks. Hair changes to a curlier pattern are usually gradual as well. Our son was no exception, and is now my hub's mini me.

My husband said he had immediately confronted and questioned the guy, who completely denied saying anything inappropriate and claimed he only said, as a joke, the baby was too cute to be my husband's. But others in the office confirmed the first coworker's account. Not only that, the guy had tried to parlay his superior perception skills into some weird form of workplace clout.

Fortunately, the guy got moved to a different shift that same week, so my husband didn't have to see him again. That is, until a company event this past weekend. Families were invited, and we took our son. And who should come and insert himself into our group as we were chatting with the boss but Brown Noser McMouth. He interrupted our conversation and introduced himself to the boss, shaking his hand.

When I realized who he was, my anger came flooding back, and I said, "I don't believe we've met, but aren't you the guy who went around telling everyone in the office I must have cheated on my husband with a white or Asian man and this couldn't be his son?" The guy went red and silent. Boss said to him, "See me in my office first thing Monday," and walked away.

I think someone's fired. My husband said I went too far because it was already over and done with. I said it wasn't done for me until I'd had my say, and I was the one being defamed, not him. AITAH?

"""

# Step 2: Convert Text to Speech
tts = gTTS(text=aita_text, lang='en')
audio_path = "voiceover.mp3"
tts.save(audio_path)

# Step 3: Generate Scrolling Text
video_width, video_height = 1080, 1920
text_clip = TextClip(aita_text, fontsize=40, color="white", size=(video_width - 100, None), method="caption")
text_clip = text_clip.set_position(("center", "bottom")).set_duration(10).scroll(y_speed=-50)  # Scrolls up

# Step 4: Add Voiceover
audio_clip = AudioFileClip(audio_path)
text_clip = text_clip.set_audio(audio_clip)

# Step 5: Export Video
output_path = "aita_video.mp4"
text_clip.write_videofile(output_path, fps=30, codec="libx264")

print(f"Video saved as {output_path}")
