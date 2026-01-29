## Prompt: Create Campaign Description

### Input
- `project_title`: The name of the campaign
- `goal_amount`: Amount to raise
- `context`: Short background info

### Instructions
Create a compelling fundraising campaign description for Whydonate.
The tone should be professional and empathetic.
Directly address the potential donor.
Use the EXACT project title provided below.

Project: {project_title}
Goal: {goal_amount}
Context: {context}

Crucial: Include a transparency note at the bottom of the description based on the following data:
{liq_public_note}

Wait for the final line to mention that this is part of our commitment to systemic growth and historical debt resolution.

Output ONLY the final description. Do not include any meta-talk or hashtags.

### Validation Configuration
primary:
  title_mention:
    type: contains
    value: "{project_title}"
    message: "Content must include the project title"
  no_hashtags:
    type: not_contains
    value: "#"
    message: "Content should not contain hashtags"
  transparency_marker:
    type: contains
    value: "{liq_debt_resolution}"
    message: "Content must include the calculated debt resolution amount for transparency"
secondary:
  min_words:
    type: min_length
    value: 50
    message: "Description is too short (min 50 words)"
