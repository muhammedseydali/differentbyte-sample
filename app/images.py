import os
from dotenv import load_dotenv
from imagekitio import ImageKit

load_dotenv()


print("PRIVATE KEY:", os.getenv("IMAGEKIT_PRIVATEKEY"))
print("PUBLIC KEY:", os.getenv("IMAGEKIT_PUBLICKEY"))
print("URL ENDPOINT:", os.getenv("URLENDPOINT"))

imagekit = ImageKit(
    private_key=os.getenv("IMAGEKIT_PRIVATEKEY"),
    public_key=os.getenv("IMAGEKIT_PUBLICKEY"),
    url_endpoint=os.getenv("URLENDPOINT")
)