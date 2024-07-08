import os.path
import modules.scripts as scripts
import gradio as gr
from modules import sd_samplers, shared
from modules.processing import Processed, process_images, StableDiffusionProcessing, create_infotext
import modules.images as images
from modules.shared import opts, cmd_opts, state
from PIL import Image
import os

class Script(scripts.Script):

    def title(self):
        return "GIF creator from Image Slice"

    def show(self, is_txt2img):
        return True

    def ui(self, is_txt2img):
        num_cuts = gr.Slider(minimum=2, maximum=8, default=2, step=1, label="Number of cuts/slices")
        gif_duration = gr.Slider(minimum=5, maximum=1000, default=150, step=5, label="GIF duration (ms)")
        ping_pong_checkbox = gr.Checkbox(label="Ping-pong animation", default=True)
        return [num_cuts, gif_duration, ping_pong_checkbox]
    
    def cut_image(self, image, num_cuts):
        width, height = image.size
        cut_width = width // num_cuts
        cut_height = height // num_cuts
        parts = []
        for i in range(num_cuts):
            for j in range(num_cuts):
                left = j * cut_width
                upper = i * cut_height
                right = left + cut_width
                lower = upper + cut_height
                parts.append(image.crop((left, upper, right, lower)))
        return parts
    
    def run(self, p, num_cuts, gif_duration, ping_pong_animation):
        proc = process_images(p)
        gens = proc.images
        save_image_tuple = images.save_image(gens[0], p.outpath_samples, "", 0, "-Original", opts.samples_format)
        save_image = save_image_tuple[0]
        image = Image.open(save_image) # Cut the image into equal parts and create a GIF with optional ping-pong animation
        cut_parts = self.cut_image(image, num_cuts)
        gif_filename = os.path.splitext(save_image)[0] + "_gif.gif"
        if ping_pong_animation:
            cut_parts = cut_parts + cut_parts[-2:0:-1]  # Create a ping-pong sequence
        cut_parts[0].save(gif_filename, format='GIF', append_images=cut_parts[1:], save_all=True, duration=gif_duration, loop=0)
        print(f"GIF created: {gif_filename}")
        os.remove(save_image) # Delete the original saved image
    
        return Processed(p, gens, 0, "")
