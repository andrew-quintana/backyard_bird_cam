import gradio as gr
import datetime

# --- Sample Data ---
BIRD_TYPES = ["Sparrow", "Robin", "Bluebird", "Cardinal", "Finch", "Hummingbird", "Chickadee", "Warbler"]
IMAGE_DATA = [
    {"id": i, "path": f"https://placehold.co/600x400?text=Bird+{i}", "type": BIRD_TYPES[i % len(BIRD_TYPES)], "date": datetime.date(2024, 4, 1) + datetime.timedelta(days=i*2), "location": "Backyard Feeder", "notes": f"Placeholder notes for bird {i}."}
    for i in range(1, 25) # Generate 24 placeholder images
]

# --- State Variables ---
# These would ideally be session-based state in a real app
# For Gradio, we often manage this through component values and events

# --- Helper Functions ---
def filter_images(bird_type_filters, date_start_str, date_end_str, search_term):
    """Filters images based on selected bird types, date range, and search term."""
    filtered = list(IMAGE_DATA) # Start with all images

    # Filter by bird type
    if bird_type_filters and isinstance(bird_type_filters, list) and len(bird_type_filters) > 0:
        filtered = [img for img in filtered if img["type"] in bird_type_filters]

    # Filter by date range
    try:
        start_date = datetime.datetime.strptime(date_start_str, "%Y-%m-%d").date() if date_start_str else None
        end_date = datetime.datetime.strptime(date_end_str, "%Y-%m-%d").date() if date_end_str else None

        if start_date:
            filtered = [img for img in filtered if img["date"] >= start_date]
        if end_date:
            filtered = [img for img in filtered if img["date"] <= end_date]
    except ValueError:
        pass # Ignore invalid date formats for now

    # Filter by search term (simple search in notes or type)
    if search_term:
        term = search_term.lower()
        filtered = [
            img for img in filtered
            if term in img["notes"].lower() or term in img["type"].lower()
        ]
    
    # Create a list of (image_path, image_label) for the gallery
    gallery_items = [(img["path"], f"{img['type']} - {img['date'].strftime('%b %d, %Y')}") for img in filtered]
    
    # If no images match, show a placeholder message or image
    if not gallery_items:
        return [[("https://placehold.co/600x400?text=No+Birds+Found", "No matching birds found")]], "No images selected", gr.update(visible=False), None, ""

    # Return the gallery items and reset/hide other components
    return gallery_items, "No images selected", gr.update(visible=False), None, ""


def display_image_metadata(evt: gr.SelectData, bird_type_filters, date_start_str, date_end_str, search_term):
    """Displays metadata for the selected image."""
    # First, get the currently filtered list of images
    # This is a bit redundant as filter_images also does this, could be optimized
    filtered_imgs = list(IMAGE_DATA)
    if bird_type_filters and isinstance(bird_type_filters, list) and len(bird_type_filters) > 0:
        filtered_imgs = [img for img in filtered_imgs if img["type"] in bird_type_filters]
    try:
        start_date = datetime.datetime.strptime(date_start_str, "%Y-%m-%d").date() if date_start_str else None
        end_date = datetime.datetime.strptime(date_end_str, "%Y-%m-%d").date() if date_end_str else None
        if start_date:
            filtered_imgs = [img for img in filtered_imgs if img["date"] >= start_date]
        if end_date:
            filtered_imgs = [img for img in filtered_imgs if img["date"] <= end_date]
    except ValueError:
        pass
    if search_term:
        term = search_term.lower()
        filtered_imgs = [
            img for img in filtered_imgs
            if term in img["notes"].lower() or term in img["type"].lower()
        ]

    if evt.index is not None and evt.index < len(filtered_imgs):
        selected_image_data = filtered_imgs[evt.index]
        metadata_html = f"""
        <div style='font-family: sans-serif; padding: 10px; background-color: #f9f9f9; border-radius: 8px; border: 1px solid #e0e0e0;'>
            <h4 style='color: #33691e; margin-top:0;'>{selected_image_data['type']}</h4>
            <img src='{selected_image_data['path']}' style='width:100%; max-width:280px; border-radius: 4px; margin-bottom:10px;'/>
            <p><strong>Date:</strong> {selected_image_data['date'].strftime('%B %d, %Y')}</p>
            <p><strong>Location:</strong> {selected_image_data['location']}</p>
            <p><strong>Notes:</strong></p>
            <p style='background-color: #fff; padding: 8px; border-radius: 4px; border: 1px solid #eee;'>{selected_image_data['notes']}</p>
        </div>
        """
        return metadata_html
    return "<p style='padding:10px; color:#555;'>Click an image to see details.</p>"


def update_selection_info(gallery_input: gr.SelectData):
    """Updates the selection toolbar based on selected images in the gallery."""
    if gallery_input and gallery_input.selected_indices:
        count = len(gallery_input.selected_indices)
        label = f"{count} image{'s' if count > 1 else ''} selected"
        return label, gr.update(visible=True)
    return "No images selected", gr.update(visible=False)

def download_selected(gallery_input: gr.SelectData, bird_type_filters, date_start_str, date_end_str, search_term):
    # This is a placeholder. In a real app, you'd zip and provide these images.
    # For now, it just prints the paths of selected images to the console.
    filtered_imgs = list(IMAGE_DATA)
    if bird_type_filters and isinstance(bird_type_filters, list) and len(bird_type_filters) > 0:
        filtered_imgs = [img for img in filtered_imgs if img["type"] in bird_type_filters]
    try:
        start_date = datetime.datetime.strptime(date_start_str, "%Y-%m-%d").date() if date_start_str else None
        end_date = datetime.datetime.strptime(date_end_str, "%Y-%m-%d").date() if date_end_str else None
        if start_date:
            filtered_imgs = [img for img in filtered_imgs if img["date"] >= start_date]
        if end_date:
            filtered_imgs = [img for img in filtered_imgs if img["date"] <= end_date]
    except ValueError:
        pass
    if search_term:
        term = search_term.lower()
        filtered_imgs = [
            img for img in filtered_imgs
            if term in img["notes"].lower() or term in img["type"].lower()
        ]

    selected_paths = []
    if gallery_input and gallery_input.selected_indices:
        for idx in gallery_input.selected_indices:
            if idx < len(filtered_imgs):
                selected_paths.append(filtered_imgs[idx]["path"])
    
    if selected_paths:
        print(f"Download requested for: {selected_paths}")
        return gr.Info(f"Download initiated for {len(selected_paths)} image(s)! (Placeholder - check console)")
    return gr.Warning("No images selected for download.")

def relabel_selected(gallery_input: gr.SelectData):
    # Placeholder for relabeling functionality
    if gallery_input and gallery_input.selected_indices:
        count = len(gallery_input.selected_indices)
        print(f"Relabel button clicked for {count} image(s).")
        return gr.Info(f"Relabel action for {count} image(s). (Placeholder)")
    return gr.Warning("No images selected to relabel.")


# --- Custom CSS for Spring Theme ---
# Inspired by the V0.dev export colors:
# Background: from-[#f0f9ff] to-[#e8f5e9]
# Primary text/accent: #33691e, #558b2f
# Buttons/Highlights: #8bc34a, #7cb342
# Borders/Subtle UI: #d1e8cf, #f1f8e9
CUSTOM_CSS = """
body {
    background: linear-gradient(to bottom, #f0f9ff, #e8f5e9);
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
.gradio-container {
    background-color: transparent !important; /* Make overall container transparent */
}
/* App Title */
.app-title {
    text-align: center;
    color: #33691e; /* Dark green */
    font-size: 2.5em !important;
    font-weight: bold;
    padding: 15px 0px !important;
    margin-bottom: 0px !important; /* Reduce space below title */
}
.app-subtitle {
    text-align: center;
    color: #558b2f; /* Medium green */
    font-size: 1.1em !important;
    margin-top: -10px !important; /* Pull subtitle up */
    margin-bottom: 20px !important;
}

/* Sidebar styling */
.filter-sidebar .gradio-box { /* Targetting Gradio Box within the class */
    background-color: #fafff7 !important; /* Very light green/off-white */
    border-radius: 12px !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important;
    border: 1px solid #d1e8cf !important; /* Light green border */
    padding: 20px !important;
}
.filter-sidebar h2 { /* Section headers in sidebar */
    color: #33691e;
    font-size: 1.4em !important;
    margin-bottom: 12px !important;
    border-bottom: 2px solid #e0f0d8;
    padding-bottom: 8px;
}
.filter-sidebar .gradio-checkbox-group label span { /* Checkbox labels */
    color: #4f7a28;
    font-size: 1.0em !important;
}
.filter-sidebar .gradio-checkbox-group input[type="checkbox"] { /* Checkboxes */
    accent-color: #8bc34a; /* Spring green */
}
.filter-sidebar .gradio-textbox input[type="text"], .filter-sidebar .gradio-textbox input[type="date"] { /* Text/Date inputs in sidebar */
    border: 1px solid #aed581 !important; /* Lighter green border */
    border-radius: 6px !important;
    padding: 10px !important;
    background-color: #fff !important;
}
.filter-sidebar .gradio-button { /* Buttons in sidebar */
    background-color: #8bc34a !important; /* Spring green */
    color: white !important;
    border-radius: 8px !important;
    border: none !important;
    font-weight: bold !important;
}
.filter-sidebar .gradio-button:hover {
    background-color: #7cb342 !important; /* Darker spring green */
}


/* Main panel styling */
.main-panel .gradio-box {
    background-color: #fdfdfd !important; /* Slightly off-white for main content area */
    border-radius: 12px !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
    border: 1px solid #e0e0e0 !important;
    padding: 20px !important;
}

/* Gallery styling */
.image-gallery .gradio-gallery { /* The gallery itself */
    background-color: #f5fcf2 !important; /* Very light green tint for gallery background */
    border-radius: 8px !important;
    padding: 15px !important;
    border: 1px solid #e0f0d8;
}
.image-gallery .gradio-gallery img { /* Images in gallery */
    border-radius: 8px !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1) !important;
    transition: transform 0.2s ease-in-out;
}
.image-gallery .gradio-gallery img:hover {
    transform: scale(1.03);
}
.image-gallery .gradio-gallery .gallery-item { /* Container for image and checkbox */
    position: relative !important; /* Needed for absolute positioning of checkbox */
    border: none !important; /* Remove default gallery item border */
    box-shadow: none !important; /* Remove default gallery item shadow */
    background: transparent !important; /* Remove default background */
}

/* Selection Toolbar - specific styling for this row */
.selection-toolbar-row {
    background-color: #ffffff;
    padding: 10px 15px;
    border-radius: 8px;
    margin-bottom: 15px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    border: 1px solid #d1e8cf;
}
.selection-toolbar-row .gradio-html p { /* For the selected count text */
    color: #558b2f !important;
    font-weight: bold !important;
    font-size: 1.0em !important;
    margin: 0 !important; /* Remove default margins */
    display: flex;
    align-items: center;
    height: 100%;
}
.selection-toolbar-row .gradio-button {
    background-color: #8bc34a !important;
    color: white !important;
    border: none !important;
    padding: 8px 15px !important;
    font-size: 0.9em !important;
}
.selection-toolbar-row .gradio-button:hover {
    background-color: #7cb342 !important;
}
.selection-toolbar-row .relabel-button { /* Example of specific button styling */
    background-color: #ffb74d !important; /* Orange for relabel */
}
.selection-toolbar-row .relabel-button:hover {
    background-color: #ffa726 !important;
}


/* Metadata Panel Styling */
.metadata-panel .gradio-html {
    background-color: #fafff7 !important;
    border-radius: 8px !important;
    border: 1px solid #d1e8cf !important;
    padding: 15px !important;
    min-height: 300px; /* Give it some initial height */
}
.metadata-panel .gradio-html h4 {
    color: #33691e !important;
    margin-top: 0 !important;
    font-size: 1.3em !important;
    border-bottom: 1px solid #e0f0d8;
    padding-bottom: 5px;
    margin-bottom: 10px;
}
.metadata-panel .gradio-html p {
    color: #558b2f !important;
    font-size: 0.95em !important;
    line-height: 1.6 !important;
}
.metadata-panel .gradio-html strong {
    color: #33691e !important;
}
.metadata-panel .gradio-html img {
    width: 100% !important;
    max-width: 280px !important;
    border-radius: 4px !important;
    margin-bottom: 10px !important;
    border: 1px solid #d1e8cf;
}
"""

# --- Gradio UI ---
with gr.Blocks(theme=gr.themes.Soft(primary_hue="lime", secondary_hue="green"), css=CUSTOM_CSS) as demo:
    # Hidden state for selected image (to pass its data) or other complex states
    # For gallery selection, we'll use SelectData event
    
    gr.HTML("<div class='app-title'>Backyard Bird Platform</div><div class='app-subtitle'>Your Personal Bird Photo Gallery & Insights</div>")

    with gr.Row():
        # --- Left Column: Filters ---
        with gr.Column(scale=1, min_width=280, elem_classes="filter-sidebar"):
            with gr.Box():
                gr.Markdown("## Filters")
                
                gr.Markdown("### Bird Types")
                bird_type_checkboxes = gr.CheckboxGroup(choices=BIRD_TYPES, label="Select bird types to display")

                gr.Markdown("### Date Range")
                # Using Textbox for date input, as Gradio's Date component might not be as flexible for range
                # Placeholder for a more advanced date range slider if possible
                today_str = datetime.date.today().strftime("%Y-%m-%d")
                sixty_days_ago_str = (datetime.date.today() - datetime.timedelta(days=60)).strftime("%Y-%m-%d")
                
                date_start_input = gr.Textbox(label="Start Date (YYYY-MM-DD)", value=sixty_days_ago_str, placeholder="e.g., 2024-01-01")
                date_end_input = gr.Textbox(label="End Date (YYYY-MM-DD)", value=today_str, placeholder="e.g., 2024-03-31")

                gr.Markdown("### Search")
                search_input = gr.Textbox(label="Search in notes or type", placeholder="e.g., cardinal, feeder visit")
                
                # Apply Filters Button (though ideally updates are live or on input change)
                # For simplicity, we'll make gallery update on any filter change.

        # --- Main Panel: Image Grid & Details ---
        with gr.Column(scale=3, elem_classes="main-panel"):
            with gr.Box():
                # Selection Toolbar (conditionally visible)
                with gr.Row(visible=False, elem_classes="selection-toolbar-row") as selection_toolbar:
                    selected_images_label = gr.HTML("<p>No images selected</p>") # Use HTML for better styling control
                    download_button = gr.Button("Download Selected", icon="https://img.icons8.com/ios-filled/50/000000/download.png")
                    relabel_button = gr.Button("Relabel", icon="https://img.icons8.com/ios-filled/50/000000/tags.png", elem_classes="relabel-button")
                    # Add other action buttons here if needed

                # Image Gallery
                gr.Markdown("## Bird Photo Grid", elem_classes="gallery-title")
                image_gallery = gr.Gallery(
                    label="Bird Images",
                    show_label=False,
                    columns=4, # Adjust number of columns as needed
                    height="auto",
                    object_fit="cover", # Or "contain"
                    allow_preview=True, # This handles the click-to-enlarge, but we want custom metadata panel
                    show_share_button=False,
                    show_download_button=False, # We have a custom one
                    elem_classes="image-gallery" # For specific CSS targeting
                )
                # The gallery will take a list of (image_path, label_or_None) tuples
                # We will manage selections through the .select() event

        # --- Right Column: Metadata/Details Panel ---
        with gr.Column(scale=1.5, min_width=320, elem_classes="metadata-panel"):
            with gr.Box():
                gr.Markdown("## Image Details")
                metadata_display = gr.HTML("<p style='padding:10px; color:#555;'>Click an image to see details.</p>")


    # --- Event Handling ---
    filter_inputs = [bird_type_checkboxes, date_start_input, date_end_input, search_input]
    gallery_outputs = [image_gallery, selected_images_label, selection_toolbar, metadata_display, search_input] # Reset metadata and search

    # When any filter changes, update the gallery
    for fi_input in filter_inputs:
        fi_input.change(
            fn=filter_images,
            inputs=filter_inputs,
            outputs=gallery_outputs
        )
    
    # When an image in the gallery is clicked (selected for metadata view)
    # Note: Gallery's .select() gives evt.index for single click, evt.selected_indices for multi-select mode (if enabled)
    # For metadata, we care about the single clicked image.
    image_gallery.select(
        fn=display_image_metadata,
        inputs=[bird_type_checkboxes, date_start_input, date_end_input, search_input], # Pass current filters to correctly identify the image
        outputs=[metadata_display],
        # show_progress="minimal" # Removed this line as it was causing an error.
    )

    # When the gallery selection changes (for the selection toolbar)
    # This uses `selectable=True` implicitly when a select event is attached
    # We need to ensure the gallery is configured for multi-select for the toolbar actions
    # The `select` event with `evt: gr.SelectData` provides `evt.selected_indices`
    image_gallery.select(
        fn=update_selection_info,
        inputs=[], # No direct inputs needed, will use the event data
        outputs=[selected_images_label, selection_toolbar],
        # show_progress="minimal" # Removed this line as it was causing an error.
    )
    
    # Action button events
    download_button.click(
        fn=download_selected,
        inputs=[image_gallery, bird_type_checkboxes, date_start_input, date_end_input, search_input],
        outputs=[], # Potentially a status message gr.Info/gr.Error
        # show_progress="full" # Removed this line as it was causing an error.
    )
    relabel_button.click(
        fn=relabel_selected,
        inputs=[image_gallery],
        outputs=[], # Potentially a status message
        # show_progress="full" # Removed this line as it was causing an error.
    )

    # Initial population of the gallery
    demo.load(
        fn=filter_images,
        inputs=filter_inputs, # Use initial values of filters
        outputs=gallery_outputs
    )

if __name__ == "__main__":
    demo.launch(debug=True) 