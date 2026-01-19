from openai import OpenAI
from app.config import settings
from typing import Optional
import base64


def generate_asset_description(image_data: bytes, image_format: str = "png") -> Optional[str]:
    if not settings.openai_api_key:
        raise ValueError("OpenAI API key not configured")
    
    try:
        client = OpenAI(api_key=settings.openai_api_key)
        
        base64_image = base64.b64encode(image_data).decode('utf-8')
        image_url = f"data:image/{image_format};base64,{base64_image}"
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Describe this asset image in detail, including its condition, appearance, and any notable features. Be specific about the type of device, its physical state, and any visible characteristics."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        }
                    ]
                }
            ],
            max_tokens=300
        )
        
        description = response.choices[0].message.content
        return description.strip()
    
    except Exception as e:
        raise ValueError(f"Failed to generate description: {str(e)}")
