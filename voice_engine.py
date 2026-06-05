import asyncio
import edge_tts

async def _generate(
    text,
    output_file="output.mp3",
    voice="en-US-AndrewMultilingualNeural"
):
    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate="-10%",
        pitch="-10Hz"
    )

    await communicate.save(output_file)

def generate_voice(
    text,
    output_file="output.mp3",
    voice="en-US-AndrewMultilingualNeural"
):
    asyncio.run(
        _generate(
            text=text,
            output_file=output_file,
            voice=voice
        )
    )

    return output_file