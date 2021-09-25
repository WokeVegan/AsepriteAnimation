import json
import os
import re

import pygame

_FRAME_PATTERN = re.compile(r"(\w+)\s(\w+)\s(\d+)\s?")


class Animation:
    """Handles animations created with Aseprite."""

    def __init__(self, image_directory: str, json_file: str, default_layer: str, default_tag: str):
        """
        :param image_directory: This is the path to the sprite sheet. This must be given because the json file and the
        image aren't necessarily in the same directory and the json file only contains the filename itself.
        contains the filename of the image.
        :param json_file: The filename of the json file that contains all the information about the animation.
        :param default_layer: This is the starting layer of the animation.
        :param default_tag: This is the starting tag of the animation.
        """

        self.image = None
        self.format = None
        self.image_size = None
        self.scale = None
        self.frames = {}
        self.frame_tags = {}
        self.layers = {}
        self.surface = None  # This is the surface each frame is rendered to.
        self.image_directory = image_directory
        self.current_layer = default_layer
        self.current_tag = default_tag
        self.current_frame = 0
        self.elapsed_time = 0  # time passed on current frame
        self._parse(json_file)
        self._create_surface()

    def _parse(self, filename):
        """Parses the json file that is exported with the sprite sheet."""
        with open(filename) as f:
            data = json.load(f)
        f.close()

        # Meta data
        meta = data["meta"]
        image_path = os.path.join(self.image_directory, meta["image"])
        self.image = pygame.image.load(image_path)
        self.format = meta["format"]
        self.image_size = tuple(int(x) for x in meta["size"].values())
        self.scale = int(meta["scale"])

        # Correct the formatting of frameTags and layers.
        for frame_tag in meta["frameTags"]:
            values = {"from": frame_tag["from"], "to": frame_tag["to"], "direction": frame_tag["direction"]}
            self.frame_tags[frame_tag["name"]] = values

        for layer in meta["layers"]:
            values = {"opacity": layer["opacity"], "blend_mode": layer["blendMode"]}
            self.layers[layer["name"]] = values

        # Frames
        for label, info in data["frames"].items():
            match = _FRAME_PATTERN.match(label)
            if match:
                layer, tag, frame = match.groups()
                if layer not in self.frames:
                    self.frames[layer] = {}
                if tag not in self.frames[layer]:
                    self.frames[layer][tag] = {}
                self.frames[layer][tag][int(frame)] = info

    def _get_frame(self) -> dict:
        """Returns the current frames data."""
        return self.frames[self.current_layer][self.current_tag][self.current_frame]

    def _get_frame_resolution(self) -> tuple:
        """
        Returns the current frame's width and height.
        I don't see a place where this would ever be useful. It would be pretty weird to have an animation with a
        different resolution for each frame, but just to be safe, I'm going to implement this anyway.
        """
        frame = self._get_frame()
        size = frame["sourceSize"]
        return tuple(int(v) for v in size.values())  # size will always be {"w": x, "h": x} so this is safe

    def get_tag_frame_length(self) -> int:
        """
        Returns the length of the current tag's animation cycle.

        ex. Let's say the animation has 2 tags; "walk" and "idle". walk has a 4 frame cycle and idle has a 2 frame
        cycle. If the current tag is "walk", this will return 4 and if it's "idle", this will return 2.
        """
        tag = self.frame_tags[self.current_tag]
        start = tag["from"]
        end = tag["to"]
        return end - start

    def _create_surface(self) -> None:
        """
        Whenever the animation advances to the next frame this is called.
        This creates a new surface and renders the next frame in the animation.

        TODO: Either create surfaces on init or store them after they're created.
        """
        frame = self._get_frame()
        self.surface = pygame.Surface(self._get_frame_resolution(), pygame.SRCALPHA, 32)  # adjust the size to be safe
        self.surface.fill((0, 0, 0, 0))  # make the surface transparent
        sprite_location = pygame.Rect(list(frame['frame'].values()))
        x, y, __, __ = frame["spriteSourceSize"].values()
        self.surface.blit(self.image, (x, y), sprite_location)

    def get_layer_names(self) -> tuple:
        """Returns a tuple containing all the layer names."""
        return tuple(self.layers.keys())

    def get_tag_names(self) -> tuple:
        """Returns a tuple containing all the tag names."""
        return tuple(self.frame_tags.keys())

    def change_layer(self, layer_name: str) -> None:
        """
        Changes the current layer and resets some variables.
        If the layer name is not different, this has no effect
        """
        if self.current_layer is not layer_name:
            self.current_layer = layer_name
            self.current_frame = 0
            self.elapsed_time = 0
            self._create_surface()

    def change_tag(self, tag_name: str) -> None:
        """
        Changes the current tag and resets some variables.
        If the tag name is not different, this has no effect.
        """
        if self.current_tag is not tag_name:
            self.current_tag = tag_name
            self.current_frame = 0
            self.elapsed_time = 0
            self._create_surface()

    def get_frame_duration(self) -> float:
        """Returns the amount of seconds the current frame lasts for."""
        return self._get_frame()["duration"] / 1000.0

    def update(self, delta_time: float) -> None:
        """
        Main function for updating the animation. This should be called before rendering the animation.
        Note that delta_time must be in seconds. I'm not sure if this is a standard but this is how I've always handled
        time based functionality while using pygame. This can be achieved by dividing the last game tick by 1000.
        ex. delta_time = pygame.time.Clock().tick(60) / 1000.0
        """
        self.elapsed_time += delta_time
        frame_duration = self.get_frame_duration()
        while self.elapsed_time >= frame_duration:
            self.elapsed_time -= frame_duration
            self.current_frame += 1
            if self.current_frame > self.get_tag_frame_length():
                self.current_frame = 0

            # Need to recreate the surface. It's best to do this here instead of rendering the surface every frame.
            self._create_surface()

    def get_surface(self) -> pygame.Surface:
        """Use this to get the surface instead of getting it directly with Animation.surface."""
        return self.surface
