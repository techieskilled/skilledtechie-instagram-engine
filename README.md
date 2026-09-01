# Skilled Techie Instagram Engine

Zero-cost rendering layer for the Skilled Techie Instagram content system.

## Current pipeline

- GitHub Actions runs on a schedule or manually.
- Ubuntu standard runner installs FFmpeg.
- FFmpeg renders a vertical 1080x1920 MP4.
- The rendered MP4 is stored as a workflow artifact.

## Next integrations

1. Read approved content from Airtable.
2. Render dynamic hooks, tool names, and captions into video.
3. Upload rendered media to Google Drive.
4. Publish approved media to Instagram through Composio.
5. Pull Instagram insights back into Airtable.
6. Use performance history to guide the next content batch.

No paid OpenAI API or paid video-rendering service is required for the core rendering layer.
