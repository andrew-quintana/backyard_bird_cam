# This file contains the mapping from class IDs to bird species names
# Update this file with the actual bird species from your model

BIRD_CLASSES = [
    "American Crow",
    "American Goldfinch",
    "American Robin",
    "Bald Eagle",
    "Baltimore Oriole",
    "Barn Swallow",
    "Black-capped Chickadee",
    "Blue Jay",
    "Cardinal",
    "Cedar Waxwing",
    "Chipping Sparrow",
    "Common Grackle",
    "Downy Woodpecker",
    "European Starling",
    "House Finch",
    "House Sparrow",
    "Mourning Dove",
    "Northern Mockingbird",
    "Red-bellied Woodpecker",
    "Red-winged Blackbird",
    # Add more bird species as needed
]

def get_bird_name(class_id):
    """
    Get bird species name from class ID
    
    Args:
        class_id: Integer representing the class ID
        
    Returns:
        String with bird species name or "Unknown bird" if class_id is out of range
    """
    if 0 <= class_id < len(BIRD_CLASSES):
        return BIRD_CLASSES[class_id]
    return f"Unknown bird (Class ID: {class_id})" 