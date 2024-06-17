import xml.etree.ElementTree as ET
import svgwrite
from svgwrite import cm, mm

def wrap_text(text, max_length):
    """Wrap text into lines that fit within the given max_length, including breaking long words."""
    words = text.split()
    lines = []
    current_line = []
    current_length = 0

    for word in words:
        while len(word) > max_length:
            # Add part of the long word to the current line and create a new one for the rest
            current_line.append(word[:max_length])
            lines.append(" ".join(current_line))
            word = word[max_length:]
            current_line = []
            current_length = 0

        if current_length + len(word) + (1 if current_line else 0) <= max_length:
            current_line.append(word)
            current_length += len(word) + (1 if current_line else 0)
        else:
            lines.append(" ".join(current_line))
            current_line = [word]
            current_length = len(word)

    if current_line:
        lines.append(" ".join(current_line))

    return lines

def parse_xml_to_svg(xml_file, svg_file):
    # Parse the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()
    diagrams = root.find('Diagrams')
    # Create an SVG drawing
    dwg = svgwrite.Drawing(svg_file, profile='full')

    # Define some basic styles
    activity_style = {'stroke': 'black', 'fill': 'white', 'stroke-width': 2}
    initial_node_style = {'fill': 'black'}
    final_node_style = {'fill': 'red'}
    connector_style = {'stroke': 'black', 'stroke-width': 1}
    text_max_length = 20  # Max characters per line for wrapped text

    # Map elements to positions (this is a basic layout logic, can be enhanced)
    element_positions = {}
    current_y = 20  # Starting Y position
    element_spacing = 60  # Space between elements, increased to fit text wrapping

    # Debug information
    initial_nodes_count = 0
    # Find and place InitialNode
    for initial_node in diagrams.findall(".//InitialNode"):
        id = initial_node.get('Id')
        element_positions[id] = (20, current_y)
        dwg.add(dwg.circle(center=(20, current_y), r=5, **initial_node_style))
        current_y += element_spacing
        initial_nodes_count += 1
    print(f"Total InitialNodes: {initial_nodes_count}")

    activities_count = 0
    # Find and place Activities
    for activity in diagrams.findall(".//Activity"):
        id = activity.get('Id')
        name = activity.get('Name')
        newX = int(activity.get('X'))
        newY = int(activity.get('Y'))
        wrapped_lines = wrap_text(name, text_max_length)

        rect_height = 20 + (len(wrapped_lines) - 1) * 12  # Adjust height based on wrapped lines
        element_positions[id] = (100, current_y)

        # dwg.add(dwg.rect(insert=(70, current_y - rect_height / 2), size=(200, rect_height), **activity_style))

        dwg.add(dwg.rect(insert=(70, current_y - rect_height / 2), size=(newX, rect_height), **activity_style))
        # Draw each line of the wrapped text
        for i, line in enumerate(wrapped_lines):
            # text_y = current_y - rect_height / 2 + 15 + i * 12  # Adjust Y for each line
            text_y = newY - rect_height / 2 + 15 + i * 12
            # dwg.add(dwg.text(line, insert=(170, text_y), fill='black', text_anchor='middle'))  # Adjust X to match rectangle width

            dwg.add(dwg.text(line, insert=(newX - 30, text_y), fill='black', text_anchor='middle'))  # Adjust X to match rectangle width

        current_y += element_spacing + (len(wrapped_lines) - 1) * 12  # Adjust spacing for wrapped text
        activities_count += 1
    print(f"Total Activities: {activities_count}")

    actions_count = 0
    # Find and place ActivityAction
    for action in diagrams.findall(".//ActivityAction"):
        id = action.get('Id')
        name = action.get('Name')
        background = action.get('Background', 'rgb(255, 255, 255)')  # Default to white if not specified
        wrapped_lines = wrap_text(name, text_max_length)

        rect_height = 20 + (len(wrapped_lines) - 1) * 12  # Adjust height based on wrapped lines
        element_positions[id] = (100, current_y)

        # Parse the background color from the XML
        background_style = {
            'stroke': 'black',
            'fill': background,
            'stroke-width': 2
        }

        dwg.add(dwg.rect(insert=(70, current_y - rect_height / 2), size=(200, rect_height), **background_style))

        # Draw each line of the wrapped text
        for i, line in enumerate(wrapped_lines):
            text_y = current_y - rect_height / 2 + 15 + i * 12  # Adjust Y for each line
            dwg.add(dwg.text(line, insert=(170, text_y), fill='black', text_anchor='middle'))  # Adjust X to match rectangle width

        current_y += element_spacing + (len(wrapped_lines) - 1) * 12  # Adjust spacing for wrapped text
        actions_count += 1
    print(f"Total ActivityActions: {actions_count}")

    final_nodes_count = 0
    # Find and place FinalNode
    for final_node in diagrams.findall(".//ActivityFinalNode"):
        id = final_node.get('Id')
        element_positions[id] = (20, current_y)
        dwg.add(dwg.circle(center=(20, current_y), r=5, **final_node_style))
        current_y += element_spacing
        final_nodes_count += 1
    print(f"Total ActivityFinalNodes: {final_nodes_count}")

    control_flows_count = 0
    # Find and draw ControlFlows
    for control_flow in diagrams.findall(".//ControlFlow"):
        from_id = control_flow.get('From')
        to_id = control_flow.get('To')
        if from_id in element_positions and to_id in element_positions:
            from_pos = element_positions[from_id]
            to_pos = element_positions[to_id]
            dwg.add(dwg.line(start=from_pos, end=to_pos, **connector_style))
            dwg.add(dwg.circle(center=to_pos, r=2, fill='black'))  # Adding arrow heads
            control_flows_count += 1
    print(f"Total ControlFlows: {control_flows_count}")

    # Save the SVG file
    dwg.save()


if __name__ == "__main__":
    xml_input_file = 'sumxmls/simple_activity_simple.xml'
    svg_output_file = 'diagram.svg'

    parse_xml_to_svg(xml_input_file, svg_output_file)
