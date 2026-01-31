"""Service class to facilitate uploading, saving and manipulating image files."""
import os
from io import BytesIO
from uuid import uuid4

from fastapi import UploadFile
from PIL import Image

from fork_backend.core.logging import get_logger

log = get_logger()


class ImageService:
    """
    Service class to facilitate uploading, saving and manipulating image files.
    """

    ALLOWED_IMG_EXTENSIONS = {"image/jpeg", "image/png"}
    MAX_INPUT_IMG_SIZE = 50 * 1024 * 1024  # 50MB
    THUMBNAIL_IMG_DIMENSIONS = (200, 200)
    LARGE_IMG_DIMENSIONS = (2000, 2000)
    IMAGE_STORE_PATH_LARGE = "./images/"
    IMAGE_STORE_PATH_THUMBNAIL = "./images/thumbnails/"

    def __init__(self):
        if not os.path.exists(self.IMAGE_STORE_PATH_LARGE):
            os.makedirs(self.IMAGE_STORE_PATH_LARGE)
        if not os.path.exists(self.IMAGE_STORE_PATH_THUMBNAIL):
            os.makedirs(self.IMAGE_STORE_PATH_THUMBNAIL)

    async def get_large_path(self, image_name: str) -> str:
        """
        Get file path for a large image from image name.

        :param image_name: Name of the image to get the large image path for
        :type image_name: str
        :return: Filepath of the large image
        :rtype: str
        """
        return f"{self.IMAGE_STORE_PATH_LARGE}{image_name}"

    async def get_thumbnail_path(self, image_name: str) -> str:
        """
        Get file path for a thumbnail from image name.

        :param image_name: Name of the image to get the thumbnail path for
        :type image_name: str
        :return: Filepath of the thumbnail
        :rtype: str
        """
        return f"{self.IMAGE_STORE_PATH_THUMBNAIL}{image_name}"

    async def validate_process_save(self, image_data: UploadFile) -> str:
        """
        Validate, process and finally save image_data to disk in both large and thumbnail sizes.

        :param image_data: The image to save
        :type image_data: UploadFile
        :return: filename for the saved images
        :rtype: str
        """

        try:
            await self.validate(image_data=image_data)
        except Exception as e:
            log.warning("File failed validation: %s", str(e))
            raise Exception(f"File failed validation: {str(e)}") from e

        try:
            image_tuple = await self.process(image_data=image_data)
        except Exception as e:
            log.error("File processing failed: %s", str(e))
            raise Exception(f"File processing failed: {str(e)}") from e

        try:
            filename: str = await self.save(image_tuple=image_tuple)
        except Exception as e:
            log.error("Saving file to filesystem failed: %s", str(e))
            raise Exception(
                f"Saving file to filesystem failed: {str(e)}") from e

        return filename

    async def validate(self, image_data: UploadFile) -> bool:
        """
        Validate the input file from a file upload

        :param image_data: The uploaded file
        :type image_data: UploadFile
        :return: True if file is valid. Throws if problem found.
        :rtype: bool
        """
        if image_data.content_type not in self.ALLOWED_IMG_EXTENSIONS:
            log.warning("Invalid file type. '%s' not in %s",
                        image_data.content_type, self.ALLOWED_IMG_EXTENSIONS)
            raise Exception(f"Invalid file type. '{image_data.content_type}' " +
                            f"not in {self.ALLOWED_IMG_EXTENSIONS}")

        if image_data.size > self.MAX_INPUT_IMG_SIZE:
            log.warning("Input file too large. '%s' is larger then max allowed '%s'",
                        image_data.size, self.MAX_INPUT_IMG_SIZE)
            raise Exception(f"Input file too large. '{image_data.size}' " +
                            f"is larger then max allowed '{self.MAX_INPUT_IMG_SIZE}'")

        return True

    async def process(self, image_data: UploadFile) -> tuple[Image.Image, Image.Image]:
        """
        Process UploadFile images to final formats for saving to disk.

        :param image_data: The original image data to rezise
        :type image_data: Image.Image
        :return: A tuple containing both large [0] and thumbnail [1] sized images.
        :rtype: tuple[Image, Image]
        """

        try:
            contents = await image_data.read()
            await image_data.seek(0)  # reset file pointer
            image = Image.open(BytesIO(contents))
        except Exception as e:
            log.error("File load image file: %s", str(e))
            raise Exception(f"File load image file: {str(e)}") from e

        image_wo_alpha = await self._remove_alpha(image_data=image)

        crop_img = await self._crop(image_data=image_wo_alpha)

        image_tuple = await self._rezise(image_data=crop_img)

        return image_tuple

    async def save(self, image_tuple: tuple[Image.Image, Image.Image]) -> str:
        """
        safely store file on disk

        :param image_tuple: The files to store as a tuple of (large_image, thumbnail_image)
        :type image_tuple: tuple[Image.Image, Image.Image]
        :return: filename for the saved images
        :rtype: str

        """

        large_img, thumbnail_img = image_tuple
        large_img_path, thumbnail_img_path, filename = await self._get_file_paths()

        await self._save_to_fs(image_data=large_img, save_path=large_img_path)
        await self._save_to_fs(image_data=thumbnail_img, save_path=thumbnail_img_path)

        return filename

    async def _crop(self, image_data: Image.Image):
        """
        Crop images to 1:1 aspect ration

        :param image_data: Original image data
        :type image_data: Image.Image
        :return: Image croped to 1:1 aspect ration
        :rtype: Image
        """
        width, height = image_data.size
        new_size = min(width, height)  # Take the smaller dimension
        left = (width - new_size) / 2
        top = (height - new_size) / 2
        right = (width + new_size) / 2
        bottom = (height + new_size) / 2

        ret_image = image_data.crop((left, top, right, bottom))
        return ret_image

    async def _rezise(self, image_data: Image.Image) -> tuple[Image.Image, Image.Image]:
        """
        Create resized version of the original image for both large and thumbnail sizes.

        :param image_data: The original image data to rezise
        :type image_data: Image.Image
        :return: A tuple containing both large [0] and thumbnail [1] sized images.
        :rtype: tuple[Image, Image]
        """
        large_image: Image.Image = image_data.resize(
            self.LARGE_IMG_DIMENSIONS, Image.Resampling.LANCZOS)

        thumbnail_image: Image.Image = image_data.resize(
            self.THUMBNAIL_IMG_DIMENSIONS, Image.Resampling.LANCZOS)

        return (large_image, thumbnail_image)

    async def _remove_alpha(self, image_data: Image.Image) -> Image.Image:
        """
        Remove the alpha channel if it exists.

        :param image_data: The image to process
        :type image_data: Image.Image
        :return: Image file withour alpha channel.
        :rtype: Image.Image
        """

        if image_data.mode == "P":
            # Convert to RGBA for transparency
            image_data = image_data.convert("RGBA")

        if image_data.mode in ("RGBA"):
            background = Image.new("RGB", image_data.size, (255, 255, 255))
            print(image_data.split())
            background.paste(image_data, mask=image_data.split()[3])
            combined_image = background

            final_image = combined_image.convert("RGB")
            return final_image

        final_image = image_data.convert("RGB")
        return final_image

    async def _get_file_paths(self) -> tuple[str, str, str]:
        """
        Get new save file path for large and thumbnail sized images

        :return: A tuple containing both large [0] and thumbnail [1] file paths as well as
            file name [2].
        :rtype: tuple[str, str, str]
        """
        new_filename: str = f"{uuid4()}.jpg"

        large_img_path: str = await self.get_large_path(image_name=new_filename)
        thumbnail_img_path: str = await self.get_thumbnail_path(image_name=new_filename)

        return (large_img_path, thumbnail_img_path, new_filename)

    async def _save_to_fs(self, image_data: Image.Image, save_path: str):
        """"""
        buffer = BytesIO()
        image_data.save(buffer, format="JPEG", optimize=True, quality=85)
        with open(save_path, "wb") as f:
            f.write(buffer.getvalue())

    async def delete(self, image_name: str) -> bool:
        """
        Delete both large and thumbnail images from the filesystem.

        :param image_name: Name of the image files to delete
        :type image_name: str
        :return: True if deletion was successful, False otherwise
        :rtype: bool
        """
        try:
            large_img_path = await self.get_large_path(image_name)
            thumbnail_img_path = await self.get_thumbnail_path(image_name)

            if os.path.exists(large_img_path):
                os.remove(large_img_path)

            if os.path.exists(thumbnail_img_path):
                os.remove(thumbnail_img_path)

            return True
        except Exception as e:
            log.error("Failed to delete image files: %s", str(e))
            return False
